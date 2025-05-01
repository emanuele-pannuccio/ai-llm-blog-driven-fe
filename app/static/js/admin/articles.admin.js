function createNewPost(tagify, simplemde, file_url){
  payload = {
    "title" : $("#article-title").val(),
    "body" : simplemde.value(),
    "image" : file_url,
    "category" : $("select#category").val(),
    "tags" : tagify.value.map(e => e.value),
    "created_at" : `${$("#article-date").val()} ${$("#article-time").val()}`.trim()
  }

  for (let key in payload) {
    const value = payload[key];
    const isEmptyArray = Array.isArray(value) && value.length === 0;
    const isEmptyString = typeof value === "string" && value.trim() === "";
    if (value === null || value === undefined || isEmptyString || isEmptyArray) {
      delete payload[key];
    }
  }

  Swal.fire({
    title: "Sei certo?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Salva il Post"
  }).then((result) => {
    if (result.isConfirmed) {

        Swal.fire({
          title: "Wait..",
          html: "Verifica e salvataggio in corso del post."
        })

        Swal.showLoading()
        $.ajax({
            type: 'post',
            url: backend_url+'/post/',
            data: JSON.stringify(payload),
            xhrFields: { withCredentials: true },
            contentType: "application/json",
        })
        .done(function(){
          window.location.reload()
        })
        .fail((resp)=>{
            if (resp.responseJSON?.message != undefined){
              var title_="Ci sono stati eventuali errori nella richiesta, in particolare: "+resp.responseJSON?.message
            }else if(resp.responseJSON?.errors != undefined){
              var title_="Verificare se tutti i campi siano corretti.<br/>"
              
              title_+="\n\n"+Object.keys(resp.responseJSON.errors).map(element => {
                var str = resp.responseJSON.errors[element].map(err => {
                  return `<b>${element}</b> => <i>${err}</i>`
                }).join("<br/>")
                return str
              }).join("<br/>");
            }else{
              var title_="Errore generico."
            }

            Swal.fire({
              icon: "error",
              title: "Error",
              html: title_,
            });
        })
    }
  });
}

function editPost(tagify, simplemde, file_url){
  
  payload = {
    "title" : $("#article-title").val(),
    "body" : simplemde.value(),
    "image" : file_url,
    "category" : $("select#category").val(),
    "tags" : tagify.value.map(e => e.value),
    "created_at" : `${$("#article-date").val()} ${$("#article-time").val()}`.trim(),
    "status" : $("#article-status").val()
  }

  for (let key in payload) {
    const value = payload[key];
    const isEmptyArray = Array.isArray(value) && value.length === 0;
    const isEmptyString = typeof value === "string" && value.trim() === "";
    if (value === null || value === undefined || isEmptyString || isEmptyArray) {
      delete payload[key];
    }
  }

  if (Object.keys(payload).includes("created_at")){
    payload["created_at"] += ":00"
  }

  Swal.fire({
    title: "Sei certo?",
    text: "You won't be able to revert this!",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Salva il Post"
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        title: "Wait..",
        html: "Verifica e salvataggio in corso del post."
      })

      const $postModal = $('#post-modal');

      Swal.showLoading()

      $.ajax({
          type: 'PUT',
          url: `${backend_url}/post/${$postModal.data("post-id")}`,
          data: JSON.stringify(payload),
          xhrFields: { withCredentials: true },
          contentType: "application/json",
      })
      .done(function(){
        window.location.reload()
      })
      .fail((resp)=>{
          if (resp.responseJSON?.message != undefined){
            var title_="Ci sono stati eventuali errori nella richiesta, in particolare: "+resp.responseJSON?.message
          }else if(resp.responseJSON?.errors != undefined){
            var title_="Verificare se tutti i campi siano corretti.<br/>"
            
            title_+="\n\n"+Object.keys(resp.responseJSON.errors).map(element => {
              var str = resp.responseJSON.errors[element].map(err => {
                return `<b>${element}</b> => <i>${err}</i>`
              }).join("<br/>")
              return str
            }).join("<br/>");
          }else{
            var title_="Errore generico."
          }

          Swal.fire({
            icon: "error",
            title: "Error",
            html: title_,
          });
        })
    }
  })
}

$(document).ready(function(){
    var tagify = null

    var inputElem = document.querySelector('#tag-input')
    $.get(backend_url+"/tag/").then(resp => {
      tagify = new Tagify(inputElem, {
        whitelist: resp.result.map(elem => {
          return elem.tag
        })
      })
    })

    const $uploadArea = $('#upload-area');
    const $previewContainer = $('#image-preview-container');
    const $postModal = $('#post-modal');

    // Initialize SimpleMDE editor
    const simplemde = new SimpleMDE({
        element: document.getElementById("article-content"),
        spellChecker: false,
        autosave: { enabled: false },
        toolbar: [
            "bold", "italic", "heading", "|",
            "quote", "unordered-list", "ordered-list", "|",
            "link", "image", "|",
            "preview", "side-by-side", "fullscreen", "|",
            "guide"
        ]
    });
    
    $('#add-article-btn, #close-modal, #cancel-article').on('click', () => {
        // resetModal()
        $("#post-modal input, #post-modal select").val("")
        simplemde.value("")
        $('#remove-image').click()

        $postModal.scrollTop(0)
        $postModal.toggleClass("hidden")
    });

    $('#add-article-btn').click(function(){
      $postModal.data("mode", "new")
      $postModal.data("post-id", "")
    })

    var file_url = null

    // Image upload and preview
    $('#file-upload').on('change', function(e) {
        file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                $('#image-preview').attr('src', event.target.result);
                $uploadArea.hide();
                $previewContainer.show();
            };

            const formData = new FormData();
            formData.append('image', file);

            $.ajax({
              type: 'post',
              url: '/upload',
              data: formData,
              processData: false,
              xhrFields: { withCredentials: true },
              contentType: false,
            }).done(resp => {
              file_url = resp.path
            })
            reader.readAsDataURL(file);
        }
    });

    // Remove image
    $('#remove-image').on('click', function() {
        $('#file-upload').val('');
        $('#image-preview').attr('src', '');
        $uploadArea.show();
        $previewContainer.hide();
    });

    $("#save-article").click(function(){
      const mode = $postModal.data("mode") 
      if (mode == "new") createNewPost(tagify, simplemde, file_url)
      else if(mode == "edit") editPost(tagify, simplemde, file_url)
    })    

    $("#post-table .delete-post-btn").click(function(){
      Swal.fire({
          title: "Sicuro di voler eliminare?",
          html: `Stai per eliminare il seguente post:<br/><br/><b>ID</b> -> ${$(this).parents("tr").data("id")}<br/><b>titolo</b> -> ${$(this).parents("tr").data("title")}`,
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#d33",
          cancelButtonColor: "#3085d6",
          confirmButtonText: "Elimina il Post"
      }).then((result) => {
          if (result.isConfirmed) {
              $.ajax({
                  type: 'delete',
                  url: `${backend_url}/post/${$(this).parents("tr").data("id")}`,
                  xhrFields: { withCredentials: true },
                  contentType: "application/json",
              })
              .done(() => {
                  $(this).parents("tr").remove()
                  Toast.fire({
                    title: "Post eliminato con successo.",
                    icon: "success"
                  })
              })
              .fail((resp)=>{
                  Swal.fire({
                    icon: "error",
                    title: "Error",
                    html: "È avvenuto un'errore durante la richiesta, riprovare tra qualche istante.",
                  });
              })
          }
      })
    })

    $('#post-table .edit-post-btn').click(function() {
      const $tr = $(this).parents("tr")
      const post_id = $tr.data("id")

      $postModal.data("mode", "edit")
      $postModal.data("post-id", post_id)

      $.ajax({
        type: 'get',
        url: `${backend_url}/post/${post_id}`,
        // data: JSON.stringify(payload),
        xhrFields: { withCredentials: true },
        contentType: "application/json",
      }).done(function(resp){
        console.log(resp)
        $("#article-title").val(resp["title"])
        simplemde.value(resp?.body)
        $("select#category").val(resp["category"])
        $("select#article-status").val(resp["status"])

        if (resp?.created_at){
          const [day, month, year] = resp["created_at"].split(" ")[0].split('/');
          $("#article-date").val(`${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`)
          $("#article-time").val(resp?.created_at.split(" ")[1])
        }

        tagify.addTags(resp["tags"])

        if (resp?.image != undefined){
          $('#image-preview').attr('src', resp.image);
          file_url = resp.image
        }

        $uploadArea.hide();
        $previewContainer.show();

        $postModal.scrollTop(0)
        $postModal.toggleClass("hidden")
        
        // "category" : ,
        // "tags" : tagify.value.map(e => e.value),
        // "created_at" : `${$("#article-date").val()} ${$("#article-time").val()}`.trim()
      })
      console.log($postModal.data("post-id"))
    })

    $('#flt-btn').click(function(){
      const category = $("#cat-select-flt").val()
      const status = $("#stat-select-flt").val()
      const text = $("#post-text-flt").val()

      payload = {}

      if (text != ""){
        payload["text"] = text
      }

      if (category != ""){
        payload["category"] = category
      }

      if (status != ""){
        payload["status"] = status
        if (status == "archived") payload["include_deleted"] = "true"
      }

      payload = new URLSearchParams(payload).toString()
      if(payload.trim() != window.location.href){
        console.log(payload)
        window.location = `${window.location.origin}/admin/posts?${payload}`
      }
    })

    $("#post-table .restore-post-btn").click(function(){
      Swal.fire({
        title: "Sicuro di voler ripristinare?",
        html: `Stai per ripristinare il seguente post in bozza:<br/><br/><b>ID</b> -> ${$(this).parents("tr").data("id")}<br/><b>titolo</b> -> ${$(this).parents("tr").data("title")}`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Ripristina il Post"
      }).then((result) => {
          if (result.isConfirmed) {
              $.ajax({
                  type: 'put',
                  url: `${backend_url}/post/${$(this).parents("tr").data("id")}/restore`,
                  xhrFields: { withCredentials: true },
                  contentType: "application/json",
              })
              .done(() => {
                  Toast.fire({
                    title: "Post ripristinato con successo. Sincronizzazione in corso",
                    icon: "success"
                  }).then(()=>window.location.reload())
              })
              .fail(()=>{
                  Swal.fire({
                    icon: "error",
                    title: "Error",
                    html: "È avvenuto un'errore durante la richiesta, riprovare tra qualche istante.",
                  });
              })
          }
      })
    })
})