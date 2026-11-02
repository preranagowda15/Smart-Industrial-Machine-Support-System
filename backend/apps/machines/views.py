from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Machine
from .serializers import MachineSerializer
from backend.apps.accounts.permissions import IsAdministrator

class MachineListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        machines = Machine.objects.filter(is_active=True).prefetch_related("manuals")
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only Administrator can register machines
        if not (request.user.role == "ADMIN" or request.user.is_superuser):
            return Response(
                {"detail": "Only Administrators can register new machines."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = MachineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        machine = serializer.save()
        return Response(MachineSerializer(machine).data, status=status.HTTP_201_CREATED)

class MachineDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        machine = get_object_or_404(Machine, pk=pk)
        return Response(MachineSerializer(machine).data)

    def patch(self, request, pk):
        if not (request.user.role == "ADMIN" or request.user.is_superuser):
            return Response(
                {"detail": "Only Administrators can edit machine details."},
                status=status.HTTP_403_FORBIDDEN
            )
        machine = get_object_or_404(Machine, pk=pk)
        serializer = MachineSerializer(machine, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        machine = serializer.save()
        return Response(MachineSerializer(machine).data)

