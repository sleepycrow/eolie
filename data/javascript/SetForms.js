formsArray = document.querySelectorAll("form");

forms_loop: for (let i = 0; i < formsArray.length; i++) {
    let form = formsArray[i];
    let inputsArray = form.querySelectorAll("input");
    for (let h = 0; h < inputsArray.length; h++) {
        let input = inputsArray[h];
        let name = input.getAttribute("name");
        if (name == "@INPUT_NAME@") {
            input.value="@USERNAME@";
        }
        if (name == "@INPUT_PASSWORD@") {
            input.value="@PASSWORD@";
            break forms_loop;
        }
    }
}
