function toggleDropdown(showDropdownId, hideDropdownId1, hideDropdownId2) {
    var showDropdown = document.getElementById(showDropdownId);
    var hideDropdown1 = document.getElementById(hideDropdownId1);
    var hideDropdown2 = document.getElementById(hideDropdownId2);

    if (showDropdown.classList.contains('show')) {
        showDropdown.classList.remove('show');
    } else {
        showDropdown.classList.add('show');
    }

    hideDropdown1.classList.remove('show');
    hideDropdown2.classList.remove('show');
}
