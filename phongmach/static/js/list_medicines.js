$(document).ready(function(){
  $('.toast').toast('show');
});
function addPhieu() {
    event.preventDefault()
    var regis_id = document.forms["thongtinbenhnhan"]["regis_id"].value;
    var symptom = document.forms["thongtinbenhnhan"]["symptom"].value;
    var predict = document.forms["thongtinbenhnhan"]["predict"].value;

    if (confirm('Xác nhận lưu thông tin?') == true) {
        fetch('/api/add-phieu', {
            method: 'post',
            body: JSON.stringify({
                'regis_id': regis_id,
                'symptom': symptom,
                'predict': predict
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(function(res) {
            console.info(res)
            return res.json()
        }).then(function(data) {
            console.info(data)
        }).catch(function(err) {
            console.error(err)
        })
    }
}
function addMedicines(id, name, price, unit_name, dosage) {
    event.preventDefault()

    if (confirm("Bạn chắc chắn chọn thuốc " + name + "?") == true) {
      fetch('/api/add-medicine', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price,
            'unit': unit_name,
            'dosage': dosage
        }),
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.info(data)
    }).catch(function(err) {
       console.error(err)
    })
    }
}
function updateMedicines(id, obj) {
    fetch('/api/update', {
        method: 'put',
        body: JSON.stringify({
            'id': id,
            'quantity': parseInt(obj.value),
        }),
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(function(res) {
        return res.json()
    }).then(function(data) {
        console.info(data)
    })
}
function deleteMedicines(id) {
    if (confirm('Bạn chắc chắn muốn xóa thuốc này?') == true) {
        fetch('/api/delete-medicines/' + id, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(function(res) {
            return res.json()
        }).then(function(data) {
            console.info(data)
            let e = document.getElementById("medicine" + id)
            e.style.display = "none"
        }).catch(function(err) {
           console.error(err)
        })
    }
}

function save() {
    if (confirm('Bạn chắc chắn muốn lưu phiếu?') == true) {
        fetch('/api/save', {
            method: 'post'
        }).then(function(res) {
            console.info(res)
            return res.json()
        }).then(function(data) {
            console.info(data)
            if (data.code == 200)
                window.location.assign('/receipt')
        }).catch(function(err) {
           console.error(err)
        })
    }
}