$(document).ready(function () {
    var counter = 0;

    $(".addBtn").on("click", function () {
        var newRow = $("<tr>");
        var cols = "";

        cols += '<td><input type="text" class="form-control" name="search_terms"/></td>';
        cols += '<td><input type="text" class="form-control" name="search_locations"/></td>';

        cols += '<td><span class="glyphicon glyphicon-minus addBtnRemove"></span></td>';

        newRow.append(cols);
        $("#tableAddRow").append(newRow);
        counter++;
    });



    $("#tableAddRow").on("click", ".addBtnRemove", function (event) {
        $(this).closest("tr").remove();
        counter -= 1
    });


});



function calculateRow(row) {
    var price = +row.find('input[name^="price"]').val();

}

function calculateGrandTotal() {
    var grandTotal = 0;
    $("table.order-list").find('input[name^="price"]').each(function () {
        grandTotal += +$(this).val();
    });
    $("#grandtotal").text(grandTotal.toFixed(2));
}