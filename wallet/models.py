from django.db import models
from django.conf import settings
import uuid


class Wallet(models.Model):
    id = models.AutoField(primary_key=True)  # ✅ Primary Key
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wallet_id = models.CharField(max_length=20, unique=True, editable=False)  # ✅ Custom Wallet ID
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # ✅ Optional
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)      # ✅ Optional

    def save(self, *args, **kwargs):
        if not self.wallet_id:
            self.wallet_id = f"WAL{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def credit(self, amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.email} - Wallet: ₹{self.balance} ({self.wallet_id})"

    class Meta:
        db_table = "wallet_wallet"
        ordering = ['-updated_at']
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"


class WalletTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=(("CREDIT", "Credit"), ("DEBIT", "Debit"))
    )
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # ✅ Optional
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)      # ✅ Optional

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} ({self.transaction_id})"

    class Meta:
        db_table = "wallet_transactions"
        ordering = ['-created_at']
        verbose_name = "Wallet Transaction"
        verbose_name_plural = "Wallet Transactions"
