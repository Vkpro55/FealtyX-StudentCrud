from rest_framework import serializers
from .models import Student
import re

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

    # Field-level validation for email
    def validate_email(self, value):
        # Check if email format is valid
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        
        # If we are creating a new student, check for uniqueness
        if not self.instance:  # Instance is None for a create operation
            if Student.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email is already in use.")
        else:
            # If we are updating, check for uniqueness excluding the current student
            if Student.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Email is already in use.")
        
        return value

    # Field-level validation for name
    def validate_name(self, value):
        if not value.strip():  # Check if the name is not just whitespace
            raise serializers.ValidationError("Name cannot be empty.")
            
        if len(value) < 3:  # Optional: Check if name is at least 3 characters long
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        
        # If we are creating a new student, check for uniqueness
        if not self.instance:  # Instance is None for a create operation
            if Student.objects.filter(name=value).exists():
                raise serializers.ValidationError("Name is already in use.")
        else:
            # If we are updating, check for uniqueness excluding the current student
            if Student.objects.filter(name=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Name is already in use.")
        
        return value
