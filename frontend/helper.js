
function searchPhoto() {

    var apigClient = apigClientFactory.newClient();
    var user_message = document.getElementById('input-search').value;
    var params = { q: user_message };
    console.log("userMassage:", user_message)

    apigClient.searchGet(params, {}, {})
        .then(function (result) {
            console.log("result", result);
            img_paths = result["data"]["imagePaths"];
            console.log("image_paths", img_paths)
            //console.log(img_paths.substring(1,img_paths.length-1))  
            // result["data"]["body"]["imagePaths"][0]

            var div = document.getElementById("img-container");
            div.innerHTML = "";

            var j;
            for (j = 0; j < img_paths.length; j++) {
                img_ls = img_paths[j].split('/');
                img_name = img_ls[img_ls.length - 1];
                div.innerHTML += '<figure><img src="' + img_paths[j] +
                    '" style="width:50%"></figure>';
            }
        }).catch(function (result) {
            console.log()
            if (result.data== "") alert("NO Image Found!!!!")
        });
    user_message = "";
}




function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        // reader.onload = () => resolve(reader.result)
        reader.onload = () => {
            let encoded = reader.result.replace(/^data:(.*;base64,)?/, '');
            if ((encoded.length % 4) > 0) {
                encoded += '='.repeat(4 - (encoded.length % 4));
            }
            resolve(encoded);
        };
        reader.onerror = error => reject(error);
    });
}



function uploadPhoto() {

    var file = document.getElementById('file_path').files[0];
    console.log(file);

    const reader = new FileReader();

    var apigClient = apigClientFactory.newClient();
    var params = {};

    var additionalParams = {
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': file.type
        }
    }

    url = "https://dkjgsp69vl.execute-api.us-east-1.amazonaws.com/dev/upload/hx2163-nyu-cloud-photo-b2/" + file.name
    axios.put(url, file, additionalParams).then(response => {
        alert("Image uploaded: " + file.name);
    });

}

