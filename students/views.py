
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer

import requests
import json

# Create your views here.

@api_view(['POST'])
def create_student(request):

    serializer = StudentSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_students(request):
    students = Student.objects.all()

    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_student(request, id):
    
    try:
        student = Student.objects.get(pk=id)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = StudentSerializer(student)
    return Response(serializer.data)


@api_view(['PUT'])
def update_student(request, id):
    # Ensure the 'id' in the URL matches the 'id' in the request body (optional check)
    body_id = request.data.get('id')

    if body_id != str(id):  # Check if the ID in the URL matches the one in the body
        return Response({"error": "ID mismatch between URL and body."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Look for the student using the 'id' in the URL
        student = Student.objects.get(pk=id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

    # Now pass the data in the request body (excluding 'id') for updating
    serializer = StudentSerializer(student, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_student(request, id):
    try:
        student = Student.objects.get(pk=id)
        student.delete()
        return Response({"error": "Student Deleted."}, status=status.HTTP_204_NO_CONTENT)

    except Student.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def generate_student_summary(request, id):
    # Fetch the student object
    try:
        student = Student.objects.get(pk=id)
    except Student.DoesNotExist:
        return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Serialize student data
    serializer = StudentSerializer(student)
    student_data = serializer.data

    # Extract important student details
    name = student_data.get('name')
    age = student_data.get('age')
    email = student_data.get('email')
    skills = student_data.get('skills', [])
    achievements = student_data.get('achievements', [])
    hobbies = student_data.get('hobbies', [])

    # Define the Ollama API endpoint
    url = "http://localhost:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }

    # Create a more compelling and story-like prompt
    prompt = f"""
    Write a detailed and engaging story about the student profile. Include the following information:
    - Name: {name}
    - Age: {age}
    - Email: {email}
    
    Tell a story about the student’s educational journey, highlighting:
    1. Their academic achievements and accomplishments (e.g., degrees, awards).
    2. Skills they have gained (mention any programming languages, tools, or certifications).
    3. Hobbies and personal interests (e.g., activities, passions outside of academics).
    
    Make sure the summary feels personalized and interesting, as if you are telling the story of a person’s journey.
    """

    # Send the formatted request data to Ollama API
    data = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    # Make the POST request to Ollama
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Handle Ollama response
    if response.status_code == 200:
        response_text = response.text
        data = json.loads(response_text)
        actual_response = data.get("response")
        return Response({"summary": actual_response}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Failed to generate summary.", "details": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)