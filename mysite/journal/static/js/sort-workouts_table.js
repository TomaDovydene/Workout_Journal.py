document.addEventListener("DOMContentLoaded", function() {
  var table = document.querySelector(".table-bordered");
  var tableHeaders = table.querySelectorAll("th.sortable");
  var sortIcons = table.querySelectorAll(".sort-icon");
  var currentSortColumn = null;
  var isAscending = true;

  // Add click event listeners to sortable table headers
  for (var i = 0; i < tableHeaders.length; i++) {
    tableHeaders[i].addEventListener("click", sortTable.bind(null, i));
    tableHeaders[i].style.cursor = "pointer";
  }

  // Sort the table initially
  sortTable(1); // Change the index (0) to the desired default sort column index

  // Sort the table
  function sortTable(columnIndex) {
    var rows = table.querySelectorAll("tbody tr");
    var sortColumn = tableHeaders[columnIndex];

    // Toggle sort direction if it's the same column
    if (currentSortColumn === sortColumn) {
      isAscending = !isAscending;
    } else {
      // Remove sort indicator from previous column
      if (currentSortColumn !== null) {
        currentSortColumn.querySelector(".sort-icon").innerHTML = "";
      }

      // Set current sort column
      currentSortColumn = sortColumn;
      isAscending = false; // Set initial sort order to descending
    }

    // Update sort indicator
    var sortIcon = sortColumn.querySelector(".sort-icon");
    sortIcon.innerHTML = isAscending ? "&#9650;" : "&#9660;";

    // Remove sort classes from other columns
    for (var j = 0; j < tableHeaders.length; j++) {
      if (j !== columnIndex) {
        tableHeaders[j].classList.remove("asc");
        tableHeaders[j].classList.remove("desc");
      }
    }

    // Add sort classes to the current column
    sortColumn.classList.remove("asc");
    sortColumn.classList.remove("desc");
    sortColumn.classList.add(isAscending ? "asc" : "desc");

    // Convert NodeList to array for sorting
    var rowsArray = Array.prototype.slice.call(rows);

    // Sort the rows based on the column values
    rowsArray.sort(compareRows.bind(null, columnIndex));

    // Reverse the array if sorting in descending order
    if (!isAscending) {
      rowsArray.reverse();
    }

    // Re-append the sorted rows to the table body
    var tbody = table.querySelector("tbody");
    for (var k = 0; k < rowsArray.length; k++) {
      tbody.appendChild(rowsArray[k]);
    }
  }

  // Compare the values of two rows based on the column index
  function compareRows(columnIndex, rowA, rowB) {
    var valueA = rowA.cells[columnIndex].textContent;
    var valueB = rowB.cells[columnIndex].textContent;

    if (columnIndex === 0 || columnIndex === 1) {
      // Compare dates or strings
      return valueA.localeCompare(valueB);
    } else {
      // Compare numbers
      return parseFloat(valueA) - parseFloat(valueB);
    }
  }
});

