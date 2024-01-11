

class ConsultingResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_text = db.Column(db.Text)