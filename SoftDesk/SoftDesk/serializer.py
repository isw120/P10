from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Projects, Contributors, Issues, Comments


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'password')

    def validate(self, args):
        email = args.get('email', None)
        username = args.get('username', None)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'email already exists'})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': 'username already exists'})

        return super().validate(args)

    def create(self, validated_data):
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_obj = User(username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name)
        user_obj.set_password(password)
        user_obj.save()
        return validated_data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ('project_id', 'title', 'description', 'type')

    def create(self, validated_data):
        title = validated_data['title']
        description = validated_data['description']
        type = validated_data['type']
        author_user = self.context['request'].user
        project_obj = Projects(title=title,
                           description=description,
                           type=type,
                           author_user=author_user)
        print(project_obj)
        project_obj.save()
        return validated_data

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributors
        fields = ('user', 'permission', 'role')

    def create(self, validated_data):
        user = validated_data['user']
        if Projects.objects.filter(project_id=self.context['project']).exists():
            project = Projects.objects.get(project_id=self.context['project'])
        else:
            raise serializers.ValidationError("There are no project with this id")
        permission = validated_data['permission']
        role = validated_data['role']
        contributor_obj = Contributors(user=user,
                           project=project,
                           permission=permission,
                           role=role)
        contributor_obj.save()
        return validated_data

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issues
        fields = ('title', 'description', 'tag', 'priority', 'status')

    def create(self, validated_data):
        title = validated_data['title']
        description = validated_data['description']
        tag = validated_data['tag']
        priority = validated_data['priority']
        if Projects.objects.filter(project_id=self.context['project_id']).exists():
            project = Projects.objects.get(project_id=self.context['project_id'])
        else:
            raise serializers.ValidationError("There are no project with this id")
        status = validated_data['status']
        author_user = project.author_user
        assignee_user = Contributors.objects.get(user=self.context['request'].user)
        issues_obj = Issues(title=title,
                           description=description,
                           tag=tag,
                           priority=priority,
                           project=project,
                            status=status,
                            author_user=author_user,
                            assignee_user=assignee_user)
        issues_obj.save()
        return validated_data

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('description',)

    def create(self, validated_data):
        description = validated_data['description']
        author_user = Contributors.objects.get(user=self.context['request'].user)
        if not Projects.objects.filter(project_id=self.context['project_id']).exists():
            raise serializers.ValidationError("There are no project with this id")
        if Issues.objects.filter(pk=self.context['issue_id']).exists():
            issue = Issues.objects.get(pk=self.context['issue_id'])
        else:
            raise serializers.ValidationError("There are no issue with this id")
        comment_obj = Comments(description=description,
                            author_user=author_user,
                            issue=issue)
        comment_obj.save()
        return validated_data