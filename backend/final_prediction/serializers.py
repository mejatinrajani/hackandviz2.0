from rest_framework import serializers
from .models import FinalPrediction, UserPrediction, CombinedPrediction

class UserPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrediction
        fields = '__all__'

class CombinedPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CombinedPrediction
        fields = '__all__'

class FinalPredictionSerializer(serializers.ModelSerializer):
    # Assuming that FinalPrediction has foreign keys to UserPrediction and CombinedPrediction
    user_prediction = UserPredictionSerializer(read_only=True)
    combined_prediction = CombinedPredictionSerializer(read_only=True)

    class Meta:
        model = FinalPrediction
        fields = '__all__'  # You can also list specific fields if needed

    def to_representation(self, instance):
        # Optionally, you can customize how the data is serialized, for example, merging fields
        ret = super().to_representation(instance)
        # Example: Add custom field
        ret['final_prediction_message'] = f"Our analysis suggests you may be experiencing **{instance.final_prediction}**."
        return ret
