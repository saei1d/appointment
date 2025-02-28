from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Transaction, Wallet
from .serializer import TransactionSerializer, WalletSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'transaction_type', 'status']
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WalletSerializer
    
    def get_permissions(self):
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_wallet(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)