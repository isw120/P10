from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Projects, Contributors, Issues, Comments
from .serializer import SignupSerializer, ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer


class SignupAPIView(APIView):

    @staticmethod
    def post(request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Message": "User created successfully"}, status=status.HTTP_201_CREATED
            )

        return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ProjectsAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProjectSerializer

    @staticmethod
    def get(request, project_id=None):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            if project_id is not None:
                queryset = Projects.objects.filter(project_id=project_id, author_user=request.user)
                if queryset:
                    objects = ProjectSerializer(queryset, many=True)
                    return Response(objects.data, status=status.HTTP_200_OK)
                else:
                    return Response("You dont have any project with this id", status=status.HTTP_404_NOT_FOUND)
            else:
                queryset = Projects.objects.filter(author_user=request.user)
                if queryset:
                    objects = ProjectSerializer(queryset, many=True)
                    return Response(objects.data, status=status.HTTP_200_OK)
                else:
                    return Response("You didn't create any project", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"You dont have the permission to view the project(s)"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            context = {'request': request}
            serializer = ProjectSerializer(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "Message": "Project created successfully"}, status=status.HTTP_201_CREATED
                )

            return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to create a project"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, project_id):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            if Projects.objects.filter(project_id=project_id, author_user=request.user).exists():
                objects = Projects.objects.get(project_id=project_id, author_user=request.user)
                context = {'request': request}
                serializer = ProjectSerializer(objects, data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "Message": "Project updated successfully"}, status=status.HTTP_201_CREATED
                    )

                return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"You dont have any project with this id"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to update a project"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, project_id):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            if Projects.objects.filter(project_id=project_id, author_user=request.user).exists():
                Projects.objects.get(project_id=project_id).delete()
                all_issues = Issues.objects.filter(project=project_id).all()
                if all_issues is not None:
                    for issue in all_issues:
                        all_comments = Comments.objects.filter(issue=issue.id).all()
                        issue.delete()
                        if all_comments is not None:
                            for comment in all_comments:
                                comment.delete()
                return Response({
                    "Message": "Project deleted successfully"}, status=status.HTTP_200_OK
                )
            else:
                return Response({"You dont have any project with this id"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to delete a project"}, status=status.HTTP_400_BAD_REQUEST)


class ContributorsAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ContributorSerializer

    @staticmethod
    def post(request, project_id):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            context = {'project': project_id}
            serializer = ContributorSerializer(data=request.data, context=context)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({
                        "Message": "Contributor added successfully"}, status=status.HTTP_201_CREATED
                    )
                except IntegrityError:
                    return Response({
                        "Message": "This contributor is already added to this project"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to add a contributor to a project"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get(request, project_id):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            objects = ContributorSerializer(Contributors.objects.filter(project=project_id), many=True)
            if not objects.data:
                return Response("There are no contributer(s) linked to this project")
            else:
                return Response(objects.data, status=status.HTTP_200_OK)
        else:
            return Response({"You dont have the permission to view the contributor(s) linked to a project"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, project_id, contributor_id):
        if Contributors.objects.filter(user=request.user).exists() is not True:
            if Projects.objects.filter(author_user=request.user, project_id=project_id).exists():
                if Projects.objects.filter(project_id=project_id).exists() and Contributors.objects.filter(
                        user=contributor_id).exists():
                    Contributors.objects.get(project=project_id, user=contributor_id).delete()
                    all_issues = Issues.objects.filter(project=project_id).all()
                    if all_issues is not None:
                        for issue in all_issues:
                            all_comments = Comments.objects.filter(issue=issue.id).all()
                            issue.delete()
                            if all_comments is not None:
                                for comment in all_comments:
                                    comment.delete()
                else:
                    return Response({"The id of either the project or the contributor was not found"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"You dont have the permission to delete this contributor from this project"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "Message": "Contributor deleted successfully"}, status=status.HTTP_200_OK
            )
        else:
            return Response({"You dont have the permission to delete a contributor from a project"},
                            status=status.HTTP_400_BAD_REQUEST)


class IssuesAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = IssueSerializer

    @staticmethod
    def post(request, project_id):
        if Contributors.objects.filter(user=request.user).exists():
            context = {'request': request, 'project_id': project_id}
            serializer = IssueSerializer(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "Message": "Issue added successfully"}, status=status.HTTP_201_CREATED
                )

            return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to add an issue to a project"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get(request, project_id):
        objects = IssueSerializer(Issues.objects.filter(project=project_id), many=True)
        if not objects.data:
            return Response("There are no Issue(s) linked to this project")
        else:
            return Response(objects.data, status=status.HTTP_200_OK)

    @staticmethod
    def put(request, project_id, issue_id):
        if Contributors.objects.filter(user=request.user).exists():
            contributor = Contributors.objects.get(user=request.user)
            if Issues.objects.filter(pk=issue_id, assignee_user=contributor).exists():
                objects = Issues.objects.get(pk=issue_id, assignee_user=contributor)
                context = {'request': request, 'project_id': project_id}
                serializer = IssueSerializer(objects, data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "Message": "Issue updated successfully"}, status=status.HTTP_201_CREATED
                    )

                return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"You dont have the permission to update this issue"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to update an issue to a project"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, project_id, issue_id):
        if Contributors.objects.filter(user=request.user).exists():
            contributor = Contributors.objects.get(user=request.user)
            if Projects.objects.filter(project_id=project_id).exists() and Issues.objects.filter(pk=issue_id).exists():
                if Issues.objects.filter(project=project_id, pk=issue_id, assignee_user=contributor).exists():
                    issue = Issues.objects.get(project=project_id, pk=issue_id, assignee_user=contributor)
                    all_comments = Comments.objects.filter(issue=issue.id).all()
                    issue.delete()
                    if all_comments is not None:
                        for comment in all_comments:
                            comment.delete()
                    return Response({
                        "Message": "Issue deleted successfully"}, status=status.HTTP_200_OK
                    )
                else:
                    return Response({"You dont have the permission to delete this issue"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"The id of either the project or the issue was not found"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"You dont have the permission to delete an issue to a project"},
                            status=status.HTTP_400_BAD_REQUEST)


class CommentsAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CommentSerializer

    @staticmethod
    def get(request, project_id, issue_id, comment_id=None):
        if comment_id is not None:
            queryset = Comments.objects.filter(comment_id=comment_id)
            if queryset:
                objects = CommentSerializer(queryset, many=True)
                return Response(objects.data, status=status.HTTP_200_OK)
            else:
                return Response("There are no comment with this id", status=status.HTTP_404_NOT_FOUND)
        else:
            queryset = Comments.objects.filter(issue=issue_id)
            if queryset:
                objects = CommentSerializer(queryset, many=True)
                return Response(objects.data, status=status.HTTP_200_OK)
            else:
                return Response("There are no comments for this issue", status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def post(request, project_id, issue_id):
        if Contributors.objects.filter(user=request.user).exists():
            context = {'request': request, 'project_id': project_id, 'issue_id': issue_id}
            serializer = CommentSerializer(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "Message": "Comment created successfully"}, status=status.HTTP_201_CREATED
                )

            return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"You dont have the permission to create a comment to an issue"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request, project_id, issue_id, comment_id):
        if Contributors.objects.filter(user=request.user).exists():
            contributor = Contributors.objects.get(user=request.user)
            if Comments.objects.filter(comment_id=comment_id, author_user=contributor).exists():
                objects = Comments.objects.get(comment_id=comment_id, author_user=contributor)
                context = {'request': request, 'project_id': project_id, 'issue_id': issue_id}
                serializer = CommentSerializer(objects, data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        "Message": "Comment updateded successfully"}, status=status.HTTP_201_CREATED
                    )
                return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"You dont have the permission to update this comment"},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"You dont have the permission to update a comment to an issue"},
                            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, project_id, issue_id, comment_id):
        if Contributors.objects.filter(user=request.user).exists():
            contributor = Contributors.objects.get(user=request.user)
            if Projects.objects.filter(project_id=project_id).exists():
                if Issues.objects.filter(pk=issue_id).exists() and Comments.objects.filter(
                        comment_id=comment_id).exists():
                    if Comments.objects.filter(comment_id=comment_id, issue=issue_id, author_user=contributor).exists():
                        Comments.objects.get(comment_id=comment_id, issue=issue_id, author_user=contributor).delete()
                        return Response({
                            "Message": "Comment deleted successfully"}, status=status.HTTP_200_OK
                        )
                    else:
                        return Response({"You dont have the permission to delete this comment"},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"The id of either the issue or the comment was not found"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"There are no project with this id"},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"You dont have the permission to delete a comment to an issue"},
                            status=status.HTTP_400_BAD_REQUEST)
