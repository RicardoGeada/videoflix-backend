from rest_framework import serializers

from .models import CustomUser

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