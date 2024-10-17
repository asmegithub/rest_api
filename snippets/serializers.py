from rest_framework import serializers
from django.contrib.auth.models import User
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


class UserSerializer(serializers.ModelSerializer):
    # you can optionaly specify the fields you want to include in the serializer
    # in model based serializer fields and crud operations(create & update) are automatically created
    snippets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Snippet.objects.all())
    # Because 'snippets' is a reverse relationship on the User model, it will not be included by default when using the ModelSerializer class, so we needed to add an explicit field for it.

    class Meta:
        model = User
        fields = ['id', 'username', 'snippets']


class SnippetSerializer(serializers.ModelSerializer):
    # you can optionaly specify the fields you want to include in the serializer
    # in model based serializer fields and crud operations are automatically created
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'code', 'linenos',
                  'language', 'style', 'owner']

# Using HyperlinkedModelSerializer
# The HyperlinkedModelSerializer class is similar to the ModelSerializer class except that it uses hyperlinks to represent relationships, rather than primary keys.
# The HyperlinkedModelSerializer has the following differences from ModelSerializer:
#       1. It does not include the id field by default.
#       2. It includes a url field, using HyperlinkedIdentityField.
#       3. Relationships use HyperlinkedRelatedField, instead of PrimaryKeyRelatedField.
#       4. You must include the 'view_name' argument when using HyperlinkedRelatedField.
#
# We can easily re-write our existing serializers to use hyperlinking.


class SnippetHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(
        view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ['url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style']


class UserHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    # here we are using HyperlinkedRelatedField to represent the snippets relationship
    # we have to specify the view_name argument for the HyperlinkedRelatedField instead of the queryset argument

    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name='snippet-detail', read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'snippets']
