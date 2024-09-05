document.addEventListener("DOMContentLoaded", function (){
    const addQuestionButton = document.getElementById("add-question-btn");
    const questionsListInput = document.getElementById("id_quiz_questions_list");
    const questionTextInput = document.getElementById("id_quiz_question_text");
    const questionAnsw1Input = document.getElementById("id_quiz_question_answer1");
    const questionAnsw2Input = document.getElementById("id_quiz_question_answer2");
    const questionAnsw3Input = document.getElementById("id_quiz_question_answer3");
    const questionAnsw4Input = document.getElementById("id_quiz_question_answer4");

    addQuestionButton.addEventListener("click", function (event){
        event.preventDefault();
        if (!questionTextInput.value.trim()){
            alert("La domanda deve avere un contenuto.");
            return;
        }
        if (!questionAnsw1Input.value.trim() ||
            !questionAnsw2Input.value.trim() ||
            !questionAnsw3Input.value.trim() ||
            !questionAnsw4Input.value.trim()) {
            alert("Tutte le risposte devono avere un contenuto.");
            return;
        }
        const selectedCorrectAnswer = document.querySelector('input[name="quiz_question_correct_answer"]:checked');
        if (!selectedCorrectAnswer) {
            alert("Devi selezionare una risposta corretta.");
            return;
        }
        /* updating the questions list with the newly created question */
        let questionsList = [];
        try{
            questionsList = JSON.parse(questionsListInput.value || "[]");
        } catch (e) {
            console.error("Errore nel parsing della lista di domande", e);
        }
        const question = {
            question_quiz_guid: undefined,
            question_sequential: questionsList.length + 1,
            question_text: questionTextInput.value,
            question_possible_answers: [
                questionAnsw1Input.value,
                questionAnsw2Input.value,
                questionAnsw3Input.value,
                questionAnsw4Input.value
            ],
            question_correct_answer: + selectedCorrectAnswer.value
        };
        questionsList.push(question);
        questionsListInput.value = JSON.stringify(questionsList);
        console.log("Lista domande: ", questionsList);

        /* Clean the input */
        questionTextInput.value = ""
        questionAnsw1Input.value = ""
        questionAnsw2Input.value = ""
        questionAnsw3Input.value = ""
        questionAnsw4Input.value = ""
        const radioButtons = document.querySelectorAll('input[name="quiz_question_correct_answer"]');
        radioButtons.forEach(function (radio) {
            radio.checked = false;
        });
    });
});