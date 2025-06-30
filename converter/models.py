from django.db import models

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='pdfs/')
    signed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class ConversionHistory(models.Model):
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE)
    converted_at = models.DateTimeField(auto_now_add=True)
    conversion_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.document.title} - {self.conversion_type} on {self.converted_at}"