function setDeleteLink(event, id, role) {
    event.stopPropagation();
    const deleteLink = document.getElementById("delete-link");
    switch (parseInt(role)) {
        case 0:
            deleteLink.href = `customers/delete/${id}`;
            break;
        case 1:
            deleteLink.href = `managers/delete/${id}`;
            break;
        case 2:
            deleteLink.href = `admins/delete/${id}`;
            break;
        default:
            break;
    }
}
