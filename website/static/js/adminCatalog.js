function setDeleteLink(event, id) {
    event.stopPropagation();
    const deleteLink = document.getElementById("delete-link");
    deleteLink.href = `product/delete/${id}`;
}

