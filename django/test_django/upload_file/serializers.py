from rest_framework import serializers


class UploadFileSerializer(serializers.Serializer):
    file = serializers.FileField()


class AuthUserSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()
