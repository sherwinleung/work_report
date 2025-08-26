from rest_framework import serializers
from .models import WorkEntry

class WorkEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkEntry
        fields = ["id","date","start_time","end_time","title","content","duration_minutes","created_at","updated_at"]
