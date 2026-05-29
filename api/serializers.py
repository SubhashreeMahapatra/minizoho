from rest_framework import serializers
from accounts.models import User
from tasks.models import Task, TaskComment
from attendance.models import Attendance, LeaveRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','email','role','department','phone','is_active','date_of_joining']
        read_only_fields = ['id']


class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    class Meta:
        model = TaskComment
        fields = ['id','task','author','author_name','content','created_at']
        read_only_fields = ['id','author','created_at']
    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else ''


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_overdue = serializers.ReadOnlyField()
    comments = TaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id','title','description','assigned_to','assigned_to_name','created_by','created_by_name',
                  'priority','status','due_date','completed_at','tags','is_overdue','comments','created_at','updated_at']
        read_only_fields = ['id','created_by','completed_at','created_at','updated_at']

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.get_full_name() if obj.assigned_to else ''
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else ''

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    hours_worked = serializers.ReadOnlyField()
    class Meta:
        model = Attendance
        fields = ['id','user','user_name','date','check_in','check_out','status','notes','hours_worked','created_at']
        read_only_fields = ['id','created_at']
    def get_user_name(self, obj):
        return obj.user.get_full_name()


class LeaveRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    days_requested = serializers.ReadOnlyField()
    class Meta:
        model = LeaveRequest
        fields = ['id','user','user_name','leave_type','start_date','end_date','reason','status','reviewed_by','reviewed_at','days_requested','created_at']
        read_only_fields = ['id','user','reviewed_by','reviewed_at','created_at']
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
