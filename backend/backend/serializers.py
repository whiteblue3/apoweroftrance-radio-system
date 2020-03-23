from rest_framework import serializers


# class TMSentenceSerializer(serializers.ModelSerializer):
#     sentence = serializers.CharField(max_length=255)
#     language = serializers.CharField(
#         max_length=2, allow_null=True, validators=[validators.language_validator], required=True
#     )
#
#     class Meta:
#         model = TMSentence
#         fields = [
#             'sentence', 'language'
#         ]
#
#     def create(self, validated_data):
#         sentence = validated_data.get('sentence', None)
#         language = validated_data.get('language', None)
#
#         instance = TMSentence.objects.get_or_create(sentence=sentence, language=language)
#         instance.save()
#
#         return {
#             "sentence": sentence,
#             "language": language
#         }
#
#     def update(self, instance, validated_data):
#         sentence = validated_data.get('sentence', None)
#         language = validated_data.get('language', None)
#
#         instance.sentence = sentence
#         instance.language = language
#         instance.save()
#
#         return {
#             "sentence": sentence,
#             "language": language
#         }
#
#
# class TMGroupSerializer(serializers.Serializer):
#     sentence = TMSentenceSerializer(required=True, allow_null=False)
#     translated = TMSentenceSerializer(many=True, required=True, allow_null=False)
#
#     class Meta:
#         # model = TMGroup
#         fields = [
#             'sentence', 'translated'
#         ]
#
#     def create_or_update(self, instance, validated_data):
#         sentence = validated_data.pop('sentence', None)
#         translated = validated_data.pop('translated', None)
#
#         instance_sentence, _ = TMSentence.objects.get_or_create(
#             sentence=sentence["sentence"], language=sentence["language"]
#         )
#
#         if instance is None:
#             instances = TMGroup.objects.filter(
#                 translated__sentence__exact=instance_sentence.sentence,
#                 translated__language__exact=instance_sentence.language
#             )
#
#             if instances.count() > 0:
#                 instance = instances[0]
#             else:
#                 instance = TMGroup()
#                 instance.save()
#                 instance.translated.add(instance_sentence)
#
#         for translate in translated:
#             # Filter duplicated sentence insert
#             translated_sentence = TMGroup.objects.filter(
#                 translated__sentence__exact=translate["sentence"],
#                 translated__language__exact=translate["language"]
#             )
#             if translated_sentence.count() > 0:
#                 pass
#             else:
#                 instance_translate, _ = TMSentence.objects.get_or_create(
#                     sentence=translate["sentence"], language=translate["language"]
#                 )
#                 instance.translated.add(instance_translate)
#
#         instance.save()
#
#         return self.fetch(instance)
#
#     def fetch(self, instance):
#         data = []
#         for s in instance.translated.all():
#             serializer = TMSentenceSerializer(s)
#             data.append(serializer.data)
#
#         return {
#             "id": instance.id,
#             "translated": data
#         }
#
#     def create(self, validated_data):
#         return self.create_or_update(None, validated_data)
#
#     def update(self, instance, validated_data):
#         return self.create_or_update(instance, validated_data)
