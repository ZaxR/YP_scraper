$(document).ready(function () {
    $('.addBtn').on('click', function () {
        //var trID;
        //trID = $(this).closest('tr'); // table row ID
        addTableRow();
    });
     $('.addBtnRemove').click(function () {
        $(this).closest('tr').remove();
    })
    var i = 1;
    function addTableRow()
    {
        var tempTr = $('<tr><td>{{form.search_terms(class_="form-control")}}</td><td>{{form.search_terms(class_="form-control")}}</td><td><span class="glyphicon glyphicon-minus addBtnRemove" id="addBtn_' + i + '"></span></td></tr>').on('click', function () {
           //$(this).closest('tr').remove();
           $(document.body).on('click', '.TreatmentHistoryRemove', function (e) {
                $(this).closest('tr').remove();
            });
        });
        $("#tableAddRow").append(tempTr)
        i++;
    }
});