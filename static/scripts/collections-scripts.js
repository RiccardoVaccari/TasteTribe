$(document).ready(function() {
    $("#collectionCreationForm").on("submit", function(event) {
        event.preventDefault();

        var collectionCover = document.getElementById("id_collection_cover");
        var file = collectionCover.files[0];

        if (file) {
            var reader = new FileReader();
            reader.onloadend = function() {
                var base64String = reader.result;
                $("#b64_collection_cover").val(base64String);
                submitForm();
            };
            reader.readAsDataURL(file);
        } else {
            submitForm();
        }
    });

    function submitForm() {
        $.ajax({
            url: collectionURL,
            type: "POST",
            data: new FormData($("#collectionCreationForm")[0]),
            processData: false,
            contentType: false,
            success: function(response) {
                $("#collectionCreationModal").modal("hide");
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
                alert("Spiacente, si è verificato un errore in fase di creazione, riprovare!");
            }
        });
    }
});