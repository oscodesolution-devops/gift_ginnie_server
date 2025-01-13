from rest_framework import serializers


class CloudinaryImage(serializers.Field):
    def to_representation(self, value):
        if value:
            return value.url
        return None
