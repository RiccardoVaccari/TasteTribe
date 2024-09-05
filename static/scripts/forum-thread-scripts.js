$(document).ready(function() {
    $("#message-form").submit(function(event) {
        event.preventDefault(); 
        var formData = $(this).serialize();
        $.ajax({
            type: "POST",
            url: forumThreadUrl,
            data: formData,
            success: function(response) {
                try {
                    if (typeof response === 'string' || response instanceof String) {
                        response = JSON.parse(response);
                    }
                    console.log("Success:", response);
                    /* Construct and append the new message */
                    var newMessage = `
                        <div class="thread-message" id="message-${response.message_id}">
                            <div class="message-author d-flex align-items-center mb-2">
                                <img src="data:image/*;base64,${response.user_profile_pic}" alt="Avatar" class="rounded-circle me-2" width="40" height="40">
                                <div>
                                    <strong>${response.message_author}</strong><br>
                                    <small class="text-muted">${response.creation_date}</small>
                                </div>
                            </div>
                            <p class="message-content mb-3">${response.message_content}</p>
                            <div class="d-flex align-items-center mb-3">
                                <span class="like-icon me-4" data-message-id="${response.message_id}" data-interaction-type="like">
                                    <i class="fa-regular fa-thumbs-up" id="like-icon-${response.message_id}" style="color: #000000;"></i>
                                    <small>${response.likes}</small>
                                </span>
                                <span class="dislike-icon" data-message-id="${response.message_id}" data-interaction-type="dislike">
                                    <i class="fa-regular fa-thumbs-down" id="dislike-icon-${response.message_id}" style="color: #000000;"></i>
                                    <small>${response.dislikes}</small>
                                </span>
                            </div>
                        </div>
                    `;
                    $("#messages-section").append(newMessage);
                    $("#message-content").val('');
                } catch (error) {
                    console.error("Failed to parse response as JSON: ", error);
                    console.error("Response: ", response);
                }
            },
            error: function(xhr, status, error) {
                console.error("Error occurred: ", error);
                try {
                    var response = JSON.parse(xhr.responseText);
                    console.error("Server response error: ", response);
                    alert("There was an error: " + response.error);
                } catch (e) {
                    console.error("Failed to parse error response: ", xhr.responseText);
                    alert("There was an error with your submission.");
                }
            }
        });
    });

    /* Handle user like/dislike interactions */
    $(document).on('click', '.like-icon, .dislike-icon', function() {
        var messageId = $(this).data('message-id');
        var interactionType = $(this).data('interaction-type');
        $.ajax({
            type: "POST",
            url: toggleInteractionUrl, 
            data: {
                'message_id': messageId,
                'interaction_type': interactionType,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                try {
                    var messageId = response.message_id;
                    var likes = response.likes;
                    var dislikes = response.dislikes;
                    var userInteraction = response.user_interaction;
                    var likeIcon = $("#like-icon-" + messageId);
                    var dislikeIcon = $("#dislike-icon-" + messageId);
                    if (userInteraction == 1) {
                        likeIcon.removeClass("fa-regular").addClass("fa-solid").css("color", "#0a9900");
                    } else {
                        likeIcon.removeClass("fa-solid").addClass("fa-regular").css("color", "#000000");
                    }
                    if (userInteraction == -1) {
                        dislikeIcon.removeClass("fa-regular").addClass("fa-solid").css("color", "#b80000");
                    } else {
                        dislikeIcon.removeClass("fa-solid").addClass("fa-regular").css("color", "#000000");
                    }
                    likeIcon.next("small").text(likes);
                    dislikeIcon.next("small").text(dislikes);
                } catch (error) {
                    console.error("Failed to parse response as JSON: ", error);
                    console.error("Response: ", response);
                }
            },
            error: function(xhr, status, error) {
                console.error("Error occurred: ", error);
                try {
                    var response = JSON.parse(xhr.responseText);
                    console.error("Server response error: ", response);
                    alert("There was an error: " + response.error);
                } catch (e) {
                    console.error("Failed to parse error response: ", xhr.responseText);
                    alert("There was an error with your submission.");
                }
            }
        });
    });
});