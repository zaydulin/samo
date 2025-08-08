(function ($) {
  $(document).ready(function () {
    // Basic table example
    $("#basic-1").DataTable();
    $("#basic-2").DataTable({
      paging: true,
      ordering: false,
      info: false,
      autoWidth: false,
    });
    $("#basic-6").DataTable();
    $("#basic-9").DataTable({
      stateSave: true,
    });
    $("#basic-12").DataTable({
      scrollY: "40vh",
      scrollCollapse: true,
      paging: false,
    });

    // Advance init
    $(document).ready(function () {
      // row create
      $("#row_create").DataTable({
        createdRow: function (row, data, index) {
          if (data[5].replace(/[\$,]/g, "") * 1 > 150000) {
            $("td", row).eq(5).addClass("highlight");
          } else if (data[5].replace(/[\$,]/g, "") * 1 < 40000) {
            $("td", row).eq(5).addClass("danger");
          }
        },
      });
    });

    // stock result chart
    $(document).ready(function () {
      var stock_data = [
        {
          name: "ACME Gadgets",
          symbol: "AGDTS",
          last: [2.57, 2.54, 2.54, 2.56, 2.57, 2.58, 2.59],
        },
        {
          name: "Spry Media Productions",
          symbol: "SPMP",
          last: [1.12, 1.11, 1.08, 1.08, 1.09, 1.11, 1.08],
        },
        {
          name: "Widget Emporium",
          symbol: "WDEMP",
          last: [3.4, 3.39, 3.46, 3.51, 3.5, 3.48, 3.49],
        },
        {
          name: "Sole Goodman",
          symbol: "SGMAN",
          last: [16.2, 16.4, 16.36, 16.35, 16.61, 16.46, 16.19],
        },
        {
          name: "Stanler Bits and Bobs",
          symbol: "SBIBO",
          last: [82.51, 83.47, 83.4, 83.68, 83.81, 83.29, 83.72],
        },
      ];

      let table = $("#stock").DataTable({
        ajax: function (dataSent, callback, settings) {
          let data = stock_charts;
          if (data == undefined) {
            data = stock_data;
          } else {
            data = data.data;
            for (i = 0; i < data.length; i++) {
              data[i].last.push(data[i].last.shift());
            }
          }

          callback({ data: data });
        },
        paging: false,
        initComplete: function () {
          let api = this.api();
          setInterval(function () {
            api.ajax.reload();
          }, 5000);
        },
        drawCallback: function () {
          $(".sparkline")
            .map(function () {
              return $("canvas", this).length ? null : this;
            })
            .sparkline("html", {
              type: "line",
              width: "250px",
            });
        },
        columns: [
          {
            data: "name",
          },
          {
            data: "symbol",
          },
          {
            data: null,
            render: function (data, type, row, meta) {
              return row.last[row.last.length - 1].toFixed(2);
            },
          },
          {
            data: null,
            render: function (data, type, row, meta) {
              var val = (row.last[row.last.length - 1] - row.last[row.last.length - 2]).toFixed(2);
              var colour = val < 0 ? "red" : "green";
              return type === "display" ? '<span style="color:' + colour + '">' + val + "</span>" : val;
            },
          },
          {
            data: "last",
            render: function (data, type, row, meta) {
              return type === "display" ? '<span class="sparkline">' + data.toString() + "</span>" : data;
            },
          },
        ],
      });
    });
    var stock_charts = {
      data: [
        {
          name: "ACME Gadgets",
          symbol: "AGDTS",
          last: [2.56, 2.57, 2.58, 2.59, 2.57, 2.54, 2.54],
        },
        {
          name: "Spry Media Productions",
          symbol: "SPMP",
          last: [1.08, 1.09, 1.11, 1.08, 1.12, 1.11, 1.08],
        },
        {
          name: "Widget Emporium",
          symbol: "WDEMP",
          last: [3.51, 3.5, 3.48, 3.49, 3.4, 3.39, 3.46],
        },
        {
          name: "Sole Goodman",
          symbol: "SGMAN",
          last: [16.35, 16.61, 16.46, 16.19, 16.2, 16.4, 16.36],
        },
        {
          name: "Stanler Bits and Bobs",
          symbol: "SBIBO",
          last: [83.68, 83.81, 83.29, 83.72, 82.51, 83.47, 83.4],
        },
      ],
    };

    // API
    // API Data Tables
    var t = $("#API-1").DataTable();
    var counter = 10;
    $("#addRow").on("click", function () {
      t.row.add([counter + "1", counter + ".2", counter + ".3", counter + ".4", counter + ".5"]).draw(false);
      counter++;
    });
    // Automatically add a first row of data
    $("#addRow").click();
    $("#addRow").click();
    $("#addRow").click();

    //single row delete data table start here
    var deleterow = $("#row-select-delete").DataTable();
    $("#row-select-delete tbody").on("click", "tr", function () {
      if ($(this).hasClass("selected")) {
        $(this).removeClass("selected");
      } else {
        deleterow.$("tr.selected").removeClass("selected");
        $(this).addClass("selected");
      }
    });
    $("#single-row-delete-btn").on("click", function () {
      deleterow.row(".selected").remove().draw(!1);
    });
    //single row delete data table end here
    //Range plugin datatable start here
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
      var min = parseInt($("#min").val(), 10);
      var max = parseInt($("#max").val(), 10);
      var age = parseFloat(data[3]) || 0;
      if ((isNaN(min) && isNaN(max)) || (isNaN(min) && age <= max) || (min <= age && isNaN(max)) || (min <= age && age <= max)) {
        return true;
      }
      return false;
    });
    var dtage = $("#datatable-range").DataTable();
    $("#min, #max").keyup(function () {
      dtage.draw();
    });
    //Range plugin datatable end here
  });
  //child row multiple data table start here
  function format(d) {
    // d is the original data object for the row
    return `
      <table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">
        <tr>
          <td>Name:</td>
          <td>${d.name}</td>
        </tr>
        <tr>
          <td>Position:</td>
          <td>${d.position}</td>
        </tr>
        <tr>
          <td>Office:</td>
          <td>${d.office}</td>
        </tr>
        <tr>
          <td>Salary:</td>
          <td>${d.salary}</td>
        </tr>
      </table>`;
  }

  $(document).ready(function () {
    var ct = $("#API-child-row").DataTable({
      ajax: "../assets/ajax/api.txt",
      columns: [
        {
          className: "details-control",
          orderable: false,
          data: null,
          defaultContent: "",
        },
        {
          data: "name",
        },
        {
          data: "position",
        },
        {
          data: "office",
        },
        {
          data: "salary",
        },
      ],
      order: [[1, "asc"]],
    });

    $("#API-child-row tbody").on("click", "td.details-control", function () {
      var tr = $(this).closest("tr");
      var row = ct.row(tr);

      if (row.child.isShown()) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass("shown");
      } else {
        // Open this row
        row.child(format(row.data())).show();
        tr.addClass("shown");
      }
    });
  });
  //child row multiple data table end here

  // Data sources tables
  $("#data-source-1").DataTable();
  $("#data-source-2").DataTable({
    ajax: "../assets/ajax/arrays.txt",
  });
  var dataSet = [
    ["Tiger Nixon", "System Architect", "Edinburgh", "5421", "2011/04/25", "$320,800"],
    ["Garrett Winters", "Accountant", "Tokyo", "8422", "2011/07/25", "$170,750"],
    ["Ashton Cox", "Junior Technical Author", "San Francisco", "1562", "2009/01/12", "$86,000"],
    ["Cedric Kelly", "Senior Javascript Developer", "Edinburgh", "6224", "2012/03/29", "$433,060"],
    ["Airi Satou", "Accountant", "Tokyo", "5407", "2008/11/28", "$162,700"],
    ["Brielle Williamson", "Integration Specialist", "New York", "4804", "2012/12/02", "$372,000"],
    ["Herrod Chandler", "Sales Assistant", "San Francisco", "9608", "2012/08/06", "$137,500"],
    ["Rhona Davidson", "Integration Specialist", "Tokyo", "6200", "2010/10/14", "$327,900"],
    ["Colleen Hurst", "Javascript Developer", "San Francisco", "2360", "2009/09/15", "$205,500"],
    ["Sonya Frost", "Software Engineer", "Edinburgh", "1667", "2008/12/13", "$103,600"],
    ["Jena Gaines", "Office Manager", "London", "3814", "2008/12/19", "$90,560"],
    ["Quinn Flynn", "Support Lead", "Edinburgh", "9497", "2013/03/03", "$342,000"],
    ["Charde Marshall", "Regional Director", "San Francisco", "6741", "2008/10/16", "$470,600"],
    ["Haley Kennedy", "Senior Marketing Designer", "London", "3597", "2012/12/18", "$313,500"],
    ["Tatyana Fitzpatrick", "Regional Director", "London", "1965", "2010/03/17", "$385,750"],
    ["Michael Silva", "Marketing Designer", "London", "1581", "2012/11/27", "$198,500"],
    ["Paul Byrd", "Chief Financial Officer (CFO)", "New York", "3059", "2010/06/09", "$725,000"],
    ["Gloria Little", "Systems Administrator", "New York", "1721", "2009/04/10", "$237,500"],
    ["Bradley Greer", "Software Engineer", "London", "2558", "2012/10/13", "$132,000"],
    ["Dai Rios", "Personnel Lead", "Edinburgh", "2290", "2012/09/26", "$217,500"],
    ["Jenette Caldwell", "Development Lead", "New York", "1937", "2011/09/03", "$345,000"],
    ["Yuri Berry", "Chief Marketing Officer (CMO)", "New York", "6154", "2009/06/25", "$675,000"],
    ["Caesar Vance", "Pre-Sales Support", "New York", "8330", "2011/12/12", "$106,450"],
    ["Doris Wilder", "Sales Assistant", "Sidney", "3023", "2010/09/20", "$85,600"],
    ["Angelica Ramos", "Chief Executive Officer (CEO)", "London", "5797", "2009/10/09", "$1,200,000"],
    ["Gavin Joyce", "Developer", "Edinburgh", "8822", "2010/12/22", "$92,575"],
    ["Jennifer Chang", "Regional Director", "Singapore", "9239", "2010/11/14", "$357,650"],
    ["Brenden Wagner", "Software Engineer", "San Francisco", "1314", "2011/06/07", "$206,850"],
    ["Fiona Green", "Chief Operating Officer (COO)", "San Francisco", "2947", "2010/03/11", "$850,000"],
    ["Shou Itou", "Regional Marketing", "Tokyo", "8899", "2011/08/14", "$163,000"],
    ["Michelle House", "Integration Specialist", "Sidney", "2769", "2011/06/02", "$95,400"],
    ["Suki Burks", "Developer", "London", "6832", "2009/10/22", "$114,500"],
    ["Prescott Bartlett", "Technical Author", "London", "3606", "2011/05/07", "$145,000"],
    ["Gavin Cortez", "Team Leader", "San Francisco", "2860", "2008/10/26", "$235,500"],
    ["Martena Mccray", "Post-Sales support", "Edinburgh", "8240", "2011/03/09", "$324,050"],
    ["Unity Butler", "Marketing Designer", "San Francisco", "5384", "2009/12/09", "$85,675"],
  ];
  $("#data-source-3").DataTable({
    data: dataSet,
    columns: [{ title: "Name" }, { title: "Position" }, { title: "Office" }, { title: "Extn." }, { title: "Start date" }, { title: "Salary" }],
  });
  $("#data-source-4").DataTable({
    processing: true,
    serverSide: true,
    ordering: true,
    searching: true,
    ajax: "../assets/json/server-side.json",
  });
})(jQuery);
