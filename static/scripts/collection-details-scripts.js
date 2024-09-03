$(document).ready(function() {
    $(".delete-icon").on("click", function(event) {
        event.preventDefault();
        if (confirm("Sei sicuro di voler eliminare questa ricetta dalla raccolta?")) {
            var $this = $(this);
            var collectionGuid = $this.data("collection-guid");
            var recipeGuid = $this.data("recipe-guid");
            $.ajax({
                url: deleteFromCollectionUrl,
                type: "POST",
                data: {
                    "collection_guid": collectionGuid,
                    "recipe_guid": recipeGuid,
                    "csrfmiddlewaretoken": csrfToken
                },
                success: function(response) {
                    if (response.success) {
                        $this.closest("li").remove();
                    } else {
                        alert("Errore nella cancellazione della ricetta.");
                    }
                },
                error: function() {
                    alert("Errore nella richiesta di cancellazione.");
                }
            });
        }
    });
});