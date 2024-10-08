document.addEventListener("DOMContentLoaded", function (){
    /* INGREDIENT MANAGEMENT */
    const confirmAllergensBtn = document.getElementById("confirmAllergensBtn");
    let ingredientsInput = document.getElementById('id_ingredients_list');
    let currentIngredient = null;
    let currentDosage = null;

    function addIngredientToList(name, dosage, allergens) {
        let ingredientsList = [];
        try {
            ingredientsList = JSON.parse(ingredientsInput.value || "[]");
        } catch (e) {
            console.error("Errore nel parsing della lista degli ingredienti", e);
        }
        ingredientsList.push({ name, dosage, allergens });
        ingredientsInput.value = JSON.stringify(ingredientsList);

    }

    document.getElementById('add-ingredient-btn').addEventListener('click', function() {
        var ingredientName = document.getElementById('id_ingredient').value;
        var dosage = document.getElementById('id_dosage_per_person').value;
        if (ingredientName && dosage) {
            var ingredientsData = JSON.parse(ingredientsInput.value || '[]');
            checkIngredientInDb(ingredientName).then(isInDb => {
                if(isInDb){
                    addIngredientToList(ingredientName, dosage);
                    updateIngredientsList(ingredientName, dosage);
                } else {
                    currentIngredient = ingredientName;
                    currentDosage = dosage;
                    $("#allergenModal").modal("show");
                }
            }).catch(error => {
                console.error("Errore durante il controllo dell'ingrediente nel database", error);
            });
        }
    });
    ingredientsInput = document.getElementById('id_ingredients_list');
    var ingredientsData = JSON.parse(ingredientsInput.value || '[]');
    var ingredientList = document.getElementById('ingredients-list');
    ingredientsData.forEach(function(ingredient) {
        var newIngredient = document.createElement('div');
        newIngredient.className = 'row align-items-center m-2 p-1 border-top';
        newIngredient.innerHTML = `
        <div class="col-md-6">${ingredient.name}</div>
        <div class="col-md-4">${ingredient.dosage}</div>
        <div class="col-md-2">
            <button type="button" class="btn btn-outline-danger btn-sm remove-ingredient-btn">Rimuovi</button>
        </div>`;
        ingredientList.appendChild(newIngredient);
        newIngredient.querySelector('.remove-ingredient-btn').addEventListener('click', function() {
            newIngredient.remove();
            ingredientsData = ingredientsData.filter(item => item.name !== ingredient.name || item.dosage !== ingredient.dosage);
            ingredientsInput.value = JSON.stringify(ingredientsData);
        });
    });
    confirmAllergensBtn.addEventListener("click", function (event) {
        event.preventDefault();
        const selectedAllergens = Array.from(
            document.querySelectorAll("#allergenForm input:checked")
        ).map((input) => ({
            id: input.value,
            name: input.dataset.name,
        }));
        var ingredientsInput = document.getElementById('id_ingredients_list');
        var ingredientsData = JSON.parse(ingredientsInput.value || '[]');
        addIngredientToList(
                currentIngredient,
                currentDosage,
                selectedAllergens
        );
        $("#allergenModal").modal("hide");
        updateIngredientsList(currentIngredient, currentDosage);
    });

    function checkIngredientInDb(ingredient) {
        return fetch(`/check-ingredient/?ingredient=${encodeURIComponent(ingredient)}`)
            .then((response) => response.json())
            .then((data) => data.exists);
    }

    function updateIngredientsList(ingredientName, dosage){
        var ingredientList = document.getElementById('ingredients-list');
        var newIngredient = document.createElement('div');
        newIngredient.className = 'row align-items-center m-2 p-1 border-top';
        newIngredient.innerHTML = `
            <div class="col-md-6">${ingredientName}</div>
            <div class="col-md-4">${dosage}</div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger btn-sm remove-ingredient-btn">Rimuovi</button>
            </div>`;
        ingredientList.prepend(newIngredient);
        newIngredient.querySelector('.remove-ingredient-btn').addEventListener('click', function() {
            newIngredient.remove();
            ingredientsData = ingredientsData.filter(item => item.name !== ingredientName || item.dosage !== dosage);
            ingredientsInput.value = JSON.stringify(ingredientsData);
        });
        document.getElementById('id_ingredient').value = '';
        document.getElementById('id_dosage_per_person').value = '';
    }

    /* STEPS MANAGEMENT */
    document.getElementById('add-step-btn').addEventListener('click', function() {
        var stepDescription = document.getElementById('id_step_description').value.trim();
        var stepRequiredHours = document.getElementById('id_step_required_hours').value.trim();
        var stepRequiredMinutes = document.getElementById('id_step_required_minutes').value.trim();
        if (stepDescription && !(stepRequiredHours == 0 && stepRequiredMinutes == 0)) {
            var stepsList = document.getElementById('steps-list');
            var newStep = document.createElement('div');
            newStep.className = 'row align-items-center m-2 p-1 border-top';
            newStep.innerHTML = `
                <div class="col-md-6">${stepDescription}</div>
                <div class="col-md-4">${stepRequiredHours}:${stepRequiredMinutes}</div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-step-btn">Rimuovi</button>
                </div>
            `;
            stepsList.append(newStep);
            var stepsInput = document.getElementById('id_steps_list');
            var stepsData = JSON.parse(stepsInput.value || '[]');
            stepsData.push({description: stepDescription, hours: stepRequiredHours, minutes: stepRequiredMinutes});
            stepsInput.value = JSON.stringify(stepsData);
            newStep.querySelector('.remove-step-btn').addEventListener('click', function() {
                newStep.remove();
                stepsData = stepsData.filter(item => item.description !== stepDescription || item.hours !== stepRequiredHours || item.minutes !== stepRequiredMinutes);
                stepsInput.value = JSON.stringify(stepsData);
            });
            document.getElementById('id_step_description').value = '';
            document.getElementById('id_step_required_hours').value = 0;
            document.getElementById('id_step_required_minutes').value = 0;
        }
    });
    var stepsInput = document.getElementById('id_steps_list');
    var stepsData = JSON.parse(stepsInput.value || '[]');
    var stepsList = document.getElementById('steps-list');
    stepsData.forEach(function(step) {
        var newStep = document.createElement('div');
        newStep.className = 'row align-items-center m-2 p-1 border-top';
        newStep.innerHTML = `
            <div class="col-md-6">${step.description}</div>
            <div class="col-md-4">${step.hours}:${step.minutes}</div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger btn-sm remove-step-btn">Rimuovi</button>
            </div>`;
        stepsList.appendChild(newStep);
        newStep.querySelector('.remove-step-btn').addEventListener('click', function() {
            newStep.remove();
            stepsData = stepsData.filter(item => item.description !== step.description || item.hours !== step.hours || item.minutes !== step.minutes);
            stepsInput.value = JSON.stringify(stepsData);
        });
    });

    /* TAG MANAGEMENT */
    document.getElementById('add-tag-btn').addEventListener('click', function() {
        var tagName = document.getElementById('id_tag').value;
        if (tagName) {
            var tagsList = document.getElementById('tags-list');
            var newTag = document.createElement('div');
            newTag.className = 'row align-items-center m-2 p-1 border-top';
            newTag.innerHTML = `
                <div class="col-md-4">${tagName}</div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-tag-btn">Rimuovi</button>
                </div>`;
            tagsList.append(newTag);
            var tagsInput = document.getElementById('id_tags_list');
            var tagsData = JSON.parse(tagsInput.value || '[]');
            tagsData.push(tagName);
            tagsInput.value = JSON.stringify(tagsData);
            newTag.querySelector('.remove-tag-btn').addEventListener('click', function() {
                newTag.remove();
                tagsData = tagsData.filter(item => item !== tagName);
                tagsInput.value = JSON.stringify(tagsData);
            });
            document.getElementById('id_tag').value = '';
        }
    });
    var tagsInput = document.getElementById('id_tags_list');
    var tagsData = JSON.parse(tagsInput.value || '[]');
    var tagsList = document.getElementById('tags-list');
    tagsData.forEach(function(tag) {
        var newTag = document.createElement('div');
        newTag.className = 'row align-items-center m-2 p-1 border-top';
        newTag.innerHTML = `
            <div class="col-md-4">${tag}</div>
            <div class="col-md-2">
                <button type="button" class="btn btn-outline-danger btn-sm remove-tag-btn">Rimuovi</button>
            </div>
        `;
        tagsList.appendChild(newTag);
        newTag.querySelector('.remove-tag-btn').addEventListener('click', function() {
            newTag.remove();
            tagsData = tagsData.filter(item => item !== tag);
            tagsInput.value = JSON.stringify(tagsData);
        });
    });
});