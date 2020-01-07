import magic
import os
import tarfile
from zipfile import ZipFile, is_zipfile, ZipInfo

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from utils.translation import TranslatedModelAdmin
from .models import Album, Photo


def validate_uploaded_archive(uploaded_file):
    types = ["application/gzip", "application/zip", "application/x-gzip"]
    if magic.from_buffer(uploaded_file.read(1024), mime=True) not in types:
        raise ValidationError("Only zip and tar files are allowed.")


class AlbumForm(forms.ModelForm):

    # Excuse my french
    # https://stackoverflow.com/questions/4391776/django-admin-inline-forms-limit-foreign-key-queryset-to-a-set-of-values#4392047
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs and "_cover" in self.fields:
            self.fields["_cover"].queryset = Photo.objects.filter(album=self.instance)

    album_archive = forms.FileField(
        required=False,
        help_text=_(
            "Uploading a zip or tar file adds all contained images as " "photos."
        ),
        validators=[validate_uploaded_archive],
    )

    class Meta:
        exclude = ["dirname"]


def save_photo(request, archive_file, photo, album):
    # zipfile and tarfile are inconsistent
    if isinstance(photo, ZipInfo):
        photo_filename = photo.filename
        extract_file = archive_file.open
    elif isinstance(photo, tarfile.TarInfo):
        photo_filename = photo.name
        extract_file = archive_file.extractfile
    else:
        raise TypeError("'photo' must be a ZipInfo or TarInfo object.")

    # Ignore directories
    if not os.path.basename(photo_filename):
        return

    # Generate unique filename
    num = album.photo_set.count()
    filename, extension = os.path.splitext(photo_filename)
    new_filename = str(num).zfill(4) + extension

    photo_obj = Photo()
    photo_obj.album = album
    try:
        with extract_file(photo) as f:
            photo_obj.file.save(new_filename, File(f))
    except (OSError, AttributeError):
        messages.add_message(
            request, messages.WARNING, _("Ignoring {}").format(photo_filename)
        )
        photo_obj.delete()
    else:
        photo_obj.save()

        if (
            Photo.objects.filter(album=album, _digest=photo_obj._digest)
            .exclude(pk=photo_obj.pk)
            .exists()
        ):
            messages.add_message(
                request, messages.WARNING, _("{} is duplicate.").format(photo_filename)
            )
            photo_obj.delete()


class AlbumAdmin(TranslatedModelAdmin):
    list_display = ("title", "date", "num_photos", "hidden", "shareable")
    fields = ("title", "slug", "date", "hidden", "shareable", "album_archive", "_cover")
    search_fields = ("title", "date")
    list_filter = ("hidden", "shareable")
    date_hierarchy = "date"
    prepopulated_fields = {"slug": ("date", "title_en",)}
    form = AlbumForm

    def get_queryset(self, request):
        return Album.objects.annotate(photos_count=Count("photo"))

    def num_photos(self, obj):
        """Pretty-print the number of photos"""
        return obj.photos_count

    num_photos.short_description = _("Number of photos")
    num_photos.admin_order_field = "photos_count"

    def save_model(self, request, obj, form, change):
        obj.save()

        archive = form.cleaned_data.get("album_archive", None)
        if archive is None:
            return

        iszipfile = is_zipfile(archive)
        archive.seek(0)

        if iszipfile:
            with ZipFile(archive) as zip_file:
                for photo in zip_file.infolist():
                    save_photo(request, zip_file, photo, obj)
        else:
            # is_tarfile only supports filenames, so we cannot use that
            try:
                with tarfile.open(fileobj=archive) as tar_file:
                    for photo in tar_file.getmembers():
                        save_photo(request, tar_file, photo, obj)
            except tarfile.ReadError:
                raise ValueError(_("The uploaded file is not a zip or tar " "file."))

        messages.add_message(
            request,
            messages.WARNING,
            _("Full-sized photos will not be saved " "on the Thalia-website."),
        )


class PhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "album", "hidden")
    search_fields = ("file",)
    list_filter = ("album", "hidden")
    exclude = ("_digest",)

    def save_model(self, request, obj, form, change):
        obj.save()
        messages.add_message(
            request,
            messages.WARNING,
            _("Full-sized photos will not be saved " "on the Thalia-website."),
        )


admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
