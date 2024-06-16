from django.db import models
from django.core.validators import FileExtensionValidator

class UploadedFiles(models.Model):
    xes_file = models.FileField(upload_to='uploads/', validators=[FileExtensionValidator(allowed_extensions=['xes'])])
    owl_file = models.FileField(upload_to='uploads/', validators=[FileExtensionValidator(allowed_extensions=['owl', 'rdf', 'ttl'])])
    xes_content = models.TextField()
    owl_content = models.TextField()
    xes_file_path = models.CharField(max_length=255)
    owl_file_path = models.CharField(max_length=255)

    custom_ontology_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the files are uploaded
        if self.xes_file and self.owl_file:
            # Save the files first to generate the file paths
            self.xes_file.save(self.xes_file.name, self.xes_file, save=False)
            self.owl_file.save(self.owl_file.name, self.owl_file, save=False)

            # Read the file contents
            with self.xes_file.open('r') as xes_f:
                self.xes_content = xes_f.read()
            with self.owl_file.open('r') as owl_f:
                self.owl_content = owl_f.read()

            # Store the file paths
            self.xes_file_path = self.xes_file.path
            self.owl_file_path = self.owl_file.path

        super().save(*args, **kwargs)