from rest_framework import serializers

from .models import CustomUser

from .signals import password_reset_signal
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

class RegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        extra_kwargs = {'password' : {'write_only' : True}}
        
    def create(self, validated_data):
        """
        Create a new CustomUser instance with the provided validated data.

        Returns:
            CustomUser: The newly created user instance.
        """
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = CustomUser.objects.create_user(email=email, password=password)
        return user
    

         
class PasswordResetSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True)
    
    def save(self):
        email = self.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email)
            password_reset_signal.send(sender=self.__class__, user=user)
        except CustomUser.DoesNotExist:
            pass
            
            


class PasswordResetConfirmSerializer(serializers.Serializer):
    
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")
        
        if not user.is_active:
            raise serializers.ValidationError("This user account is inactive.")
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid token.")
        
        return attrs

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uidb64']).decode()
        user = CustomUser.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        
        

class ActivateAccountSerializer(serializers.Serializer):
    
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    
    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")
        
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid token.")
        
        return attrs

    def save(self):
        uid = urlsafe_base64_decode(self.validated_data['uidb64']).decode()
        user = CustomUser.objects.get(pk=uid)
        user.is_active = True
        user.save()