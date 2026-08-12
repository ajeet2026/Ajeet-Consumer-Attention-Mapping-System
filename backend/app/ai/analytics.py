from datetime import datetime


class AnalyticsSummarizer:
    @staticmethod
    def summarize_metrics(dwell_durations, attention_durations):
        """
        Summarizes dwell time and attention analytics lists.
        """
        avg_dwell = (
            sum(dwell_durations) / len(dwell_durations)
            if dwell_durations
            else 0.0
        )
        avg_attention = (
            sum(attention_durations) / len(attention_durations)
            if attention_durations
            else 0.0
        )
        max_attention = max(attention_durations) if attention_durations else 0.0

        return {
            "average_dwell_time": float(avg_dwell),
            "average_attention_time": float(avg_attention),
            "max_attention_time": float(max_attention),
            "calculated_at": datetime.utcnow(),
        }
