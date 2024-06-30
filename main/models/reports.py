from django.db import models
from django.core.exceptions import ValidationError

#pylint: disable=no-member

class Report(models.Model):
    REASON_SPAM = 'SP'
    REASON_ABUSE = 'AB'
    REASON_INAPPROPRIATE_CONTENT = 'IC'
    REASON_OTHER = 'OT'
    REASON_SCAM = 'SC'

    REASON_CHOICES = [
        (REASON_SPAM, 'Spam'),
        (REASON_ABUSE, 'Abuse'),
        (REASON_INAPPROPRIATE_CONTENT, 'Inappropriate Content'),
        (REASON_OTHER, 'Other'),
        (REASON_SCAM, 'Scam'),
    ]

    STATUS_PENDING = 'PD'
    STATUS_UNDER_REVIEW = 'UR'
    STATUS_RESOLVED = 'RS'
    STATUS_DISMISSED = 'DS'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    reported_by = models.ForeignKey(
        "NormalUser",
        on_delete=models.CASCADE,
        related_name="reports_made",
        null=True,
        blank=True,
    )
    reported_user = models.ForeignKey(
        "NormalUser",
        on_delete=models.CASCADE,
        related_name="reports_received",
        null=True,
        blank=True,
    )
    reason = models.CharField(max_length=2, choices=REASON_CHOICES, default=REASON_ABUSE)
    details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f'Report by {self.reported_by.username} against {self.reported_user.username}'

    def clean(self):
        if self.reason == self.REASON_OTHER and not self.details:
            raise ValidationError('Details are required when reason is "Other".')

    class Meta:
        unique_together = ('reported_by', 'reported_user', 'reason')
        ordering = ['-created_at']
