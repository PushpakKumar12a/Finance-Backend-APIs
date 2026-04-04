"""
FinancialRecord model.

Design decisions:
- Decimal(12,2) for amount — supports values up to 9,999,999,999.99
- Soft delete via is_deleted flag — records are never truly removed
- Custom manager filters out soft-deleted records by default
- Category is a free-text field for flexibility (not an enum)
"""

from django.conf import settings
from django.db import models

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(del_flag=False)

class Record(models.Model):
    class TxType(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='records',
        help_text='The user who created this record.',
    )
    amt = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Transaction amount (must be positive).',
    )
    type = models.CharField(
        max_length=7,
        choices=TxType.choices,
        help_text='Whether this is income or expense.',
    )
    cat = models.CharField(
        max_length=100,
        help_text='Category label, e.g. salary, groceries, rent.',
    )
    date = models.DateField(
        help_text='Date of the transaction.',
    )
    desc = models.TextField(
        blank=True,
        default='',
        help_text='Optional notes or description.',
    )
    del_flag = models.BooleanField(
        default=False,
        help_text='Soft delete flag.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['cat']),
            models.Index(fields=['date']),
            models.Index(fields=['del_flag']),
        ]

    def __str__(self):
        return f'{self.get_type_display()} | {self.cat} | {self.amt} | {self.date}'

    def soft_delete(self):
        "Mark as deleted without removing from the database."
        self.del_flag = True
        self.save(update_fields=['del_flag', 'updated_at'])
