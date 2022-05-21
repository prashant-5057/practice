from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from fcm_django.models import FCMDevice
from push_notifications.models import APNSDevice, GCMDevice
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User

from .serializers import *


def fcm_device_create(fcm_array, user, name):
    FCMDevice.objects.create(**fcm_array, user=user, name=name)


def user_access_token(user, context, is_created=False):
    refresh = RefreshToken.for_user(user)
    response = {
        "access": str(refresh.access_token),
        "user": UserSerializer(user, context=context).data,
    }
    if is_created:
        response['message'] = "User created successfully."

    return Response(response)


class CutomObtainPairView(TokenObtainPairView):
    """ Create API view for serializer class 'CustomTokenObtainPairSerializer' """
    serializer_class = CustomTokenObtainPairSerializer


class RegisterUserView(generics.GenericAPIView):
    """ Create API view for serializer class "RegisterUserSerializer" and "UserSerializer".
    This view verify all input and create new user """
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)

        if User.objects.filter(email__iexact=request.data['email']).exists():
            return Response({'error': {"email": ["Your email already register. please login with password."]}}, status=400)

        user = serializer.save()

        FCM_update = {}
        FCM_update['registration_id'] = ''
        if 'fcm_token' in request.data:
            FCM_update['registration_id'] = request.data['fcm_token']
        if 'device_type' in request.data:
            FCM_update['type'] = request.data['device_type']

        if FCM_update['registration_id'] != '':
            FCM_update['device_id'] = user.device_id
            fcm_device_create(FCM_update, user, user.full_name)
        return user_access_token(user, self.get_serializer_context(), is_created=True)


class SocialUserView(generics.GenericAPIView):
    serializer_class = SocialUserSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)

        # get_user = User.objects.filter(
        #     Q(email__iexact=request.data['email']) | (Q(email__isnull=True) & ~Q(provider_type='guest') & Q(device_id=request.data['device_id'])))

        # if get_user.exists():
        #     get_user.update(**serializer.data)
        #     return user_access_token(get_user.first(), self.get_serializer_context(), is_created=False)

        # user = serializer.save()

        FCM_update = {}
        FCM_update['registration_id'] = ''
        if 'fcm_token' in request.data:
            FCM_update['registration_id'] = request.data.get('fcm_token')
        if 'device_type' in request.data:
            FCM_update['type'] = request.data.get('device_type')
        if 'device_id' in request.data:
            FCM_update['device_id'] = request.data.get('device_id')

        if request.data['provider_type'] == 'apple':
            if 'user_identifier_key' not in request.data or request.data['user_identifier_key'] == '':
                return Response({
                    'user_identifier_key': 'Apple user identifier key is missing'
                })
            elif User.objects.filter(user_identifier_key=request.data['user_identifier_key']).exists():
                User.objects.filter(
                    user_identifier_key=request.data['user_identifier_key']).update(provider_type=request.data['provider_type'], device_id=request.data['device_id'])

                user = User.objects.filter(
                    user_identifier_key=request.data['user_identifier_key']).first()

                if FCM_update['registration_id'] != '':
                    fcm_device_create(FCM_update, user, user.email)

                return user_access_token(user, self.get_serializer_context())

            else:
                if 'email' in request.data:
                    if User.objects.filter(email__iexact=request.data['email']).exists():
                        User.objects.filter(
                            email__iexact=request.data['email']).update(provider_type=request.data['provider_type'], user_identifier_key=request.data['user_identifier_key'], device_id=request.data['device_id'])
                        user = User.objects.filter(
                            user_identifier_key=request.data['user_identifier_key']).first()

                        if FCM_update['registration_id'] != '':
                            fcm_device_create(FCM_update, user, user.email)

                        return user_access_token(user, self.get_serializer_context())

        elif User.objects.filter(email__iexact=request.data['email']).exists():
            if request.data['provider_type'] not in ['google', 'facebook', 'apple']:
                return Response({
                    "message": "Social media signin with google, facebook or apple is supported",
                })

            User.objects.filter(
                email__iexact=request.data['email']).update(provider_type=request.data['provider_type'], device_id=request.data['device_id'])

            user = User.objects.get(email__iexact=request.data['email'])
            if FCM_update['registration_id'] != '':
                fcm_device_create(FCM_update, user, user.email)

            return user_access_token(user, self.get_serializer_context())

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if FCM_update['registration_id'] != '':
            fcm_device_create(FCM_update, user, user.email)
        return user_access_token(user, self.get_serializer_context(), is_created=True)


class GuestUserView(generics.GenericAPIView):
    serializer_class = GuestUserSerializer

    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)

        get_user = User.objects.filter(
            device_id__iexact=request.data['device_id'], provider_type='guest')

        if get_user.exists():
            return user_access_token(get_user.first(), self.get_serializer_context(), is_created=False)

        user = serializer.save()

        FCM_update = {}
        FCM_update['registration_id'] = ''
        if 'fcm_token' in request.data:
            FCM_update['registration_id'] = request.data.get('fcm_token')
        if 'device_type' in request.data:
            FCM_update['type'] = request.data.get('device_type')

        if FCM_update['registration_id'] != '':
            FCM_update['device_id'] = user.device_id
            fcm_device_create(FCM_update, user, user.device_id)

        return user_access_token(user, self.get_serializer_context(), is_created=True)


class UserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, format=None):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, format=None):
        user = self.request.user
        serializer = UserUpdateSerializer(user, data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)

        get_user = User.objects.filter(id=user.id,
                                       provider_type='guest')
        if get_user.exists():
            return Response({'error': {"message": ["This user is guest user..!!"]}}, status=403)
        serializer.save()
        user_data = UserSerializer(user)
        return Response(user_data.data)

    def delete(self, request, format=None):
        user_id = self.request.user.id
        User.objects.filter(id=user_id).delete()
        return Response({"message": [f"User {user_id} deleted successfully..!!"]}, status=200)


class FeedbackAPI(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackSerializer

    def post(self, request, format=None):
        if request.data:
            _mutable = request.data._mutable
            request.data._mutable = True
            request.data['user'] = request.user.id
            request.data._mutable = _mutable

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)
        serializer.save()
        return Response(serializer.data)


class FcmTokenAPI(generics.CreateAPIView):
    serializer_class = FcmTokenSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=400)
        fcm_data = serializer.data
        user = self.request.user

        defaults = {
            'registration_id': fcm_data['registration_id']
        }
        if self.request.user.id:
            defaults['user'] = self.request.user

        try:
            if fcm_data['device_type'] == "ios":
                APNSDevice.objects.update_or_create(
                    device_id=fcm_data['device_id'], defaults=defaults)
            else:
                GCMDevice.objects.update_or_create(
                    device_id=fcm_data['device_id'], cloud_message_type='FCM', defaults=defaults)
        except:
            return Response({'error': {'device_id': ['device id is invalid']}}, status=400)

        return Response(serializer.data)


class ForgotPasswordAPI(APIView):

    def post(self, request, format=None):
        user_email = request.data['email']
        try:
            get_user = User.objects.get(email__iexact=user_email)
            password = User.objects.make_random_password()
            get_user.set_password(password)
            get_user.save()
            subject = F"Password Reset - Sapid"
            message = F"{user_email} Your Temparary Password is: {password}"

            # send the email to the recipent
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email]
            )
            return Response({'status': True})
        except User.DoesNotExist:
            return Response({'error': "Provided email doesn't exist."}, status=404)
