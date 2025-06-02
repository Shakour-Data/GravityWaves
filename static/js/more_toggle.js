function toggleMore(button) {
    const moreDesc = button.previousElementSibling;
    const shortDesc = moreDesc.previousElementSibling;
    if (moreDesc.style.display === "none") {
        moreDesc.style.display = "inline";
        button.textContent = "Less";
        shortDesc.style.display = "none";
    } else {
        moreDesc.style.display = "none";
        button.textContent = "More";
        shortDesc.style.display = "inline";
    }
}
