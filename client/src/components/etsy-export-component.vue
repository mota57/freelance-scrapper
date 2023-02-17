
<script>
import { setTransitionHooks } from 'vue';
// import ConfirmModalComponent from './confirm-modal.component.vue'
import NumberSelect from "./NumberSelect.vue";


const port = 5000;
const baseURL = 'http://localhost:'+port;
const routeURL = '/keywords';
const apiPath = baseURL + routeURL;

export default {
  components: {
    NumberSelect
    // ConfirmModalComponent
  },
  data() {
    return {
      showModal: false,
      loading: false,
      formData: {
        id: '',
        name: '',
        is_active:true
      },
      keywords: [],
      pages: 2,
      listings: 64,
      cookie_erank: '',
      optionSelected: 'Use Default',
      logContent:'',
      keyword_url:'https://www.etsy.com/search?q=@keyword&explicit=1&is_best_seller=true&ship_to=US'
    };
  },
  methods: {
    clearForm() {
      console.log('clear form');
      this.formData = { id: '', name: '' };
    },
    editKeyword(record) {
      this.formData = JSON.parse(JSON.stringify(record));
    },
    openErank() {
      window.open('https://erank.com/listing-audit/1366856938', '_blank');
    },
    onSelectOption(option) {
      this.optionSelected = option;
      if (this.optionSelected == 'Use Default') {
        this.pages = 2,
          this.listings = 64;
      } else if (this.optionSelected == 'Test') {
        this.pages = 1,
          this.listings = 4;
      }
    },
    onPagePerKeyword(page) {
      this.pages = page;
    },
    onListingPerPage(n) {
      this.listings = n;
    },
    async getKeywords() {
      try {
        let res = await axios.get(apiPath)
        this.keywords = res.data.data;
      } catch (error) {
        // eslint-disable-next-line
        console.error(error);
      }
    },
    async saveKeyword(evt) {
      this.loading = true;
      let request = (this.formData.id) ? axios.put : axios.post;
      try {
        await request(apiPath, this.formData)
        this.clearForm();
        await this.getKeywords();
      } catch (err) {
        console.log(err);
      } finally {
        this.loading = false;
      }
    },
    async deleteKeyword(evt) {
      this.showModal = true;
      this.loading = true;
      try {
        await axios.delete(apiPath + '/' + this.formData.id, this.formData)
        $('#modalDelete').modal('hide'); //close modal
        await this.getKeywords();
      } catch (err) {
        console.log(err)
      } finally {
        this.loading = false;
      }
    },
    openModalDelete(record) {
      this.formData = JSON.parse(JSON.stringify(record));
      this.showModal = true;
    },
    async exportkeywords() {
      if (this.cookie_erank == '' || this.cookie_erank == null) {
        alert('Please enter from erank\n1-click on open erank button\n2-then click on bookmark button to copy erank cookie.');
        return;
      }

      if (this.optionSelected == '' || this.optionSelected == null) {
        alert('Select an option');
        return;
      }
      await this.clearLog()
      

      this.loading = true;
      axios({
        url: apiPath + '/export2', //your url
        method: 'POST',
        data: {
          cookie_erank: this.cookie_erank,
          pages: this.pages,
          listings: this.listings
        },
        responseType: 'blob', // important
        timeout: 1000000
      }).then((response) => {
        // create file link in browser's memory
        const href = URL.createObjectURL(response.data);

        // create "a" HTML element with href to file & click
        const link = document.createElement('a');
        link.href = href;
        link.setAttribute('download', 'data.xlsx'); //or any other extension
        document.body.appendChild(link);
        link.click();

        // clean up "a" element & remove ObjectURL
        document.body.removeChild(link);
        URL.revokeObjectURL(href);
        this.loading = false;
      }, (error) => {
        this.loading = false;

        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.log(error.response.data);
          console.log(error.response.status);
          console.log(error.response.headers);
        } else if (error.request) {
          // The request was made but no response was received
          // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
          // http.ClientRequest in node.js
          console.log(error.request);
        } else {
          // Something happened in setting up the request that triggered an Error
          console.log('Error', error.message);
        }
        console.log(error.config);

        alert('an error occurred, check the console & log for more information.');
      });
    },
    async loadLog() {
      this.loading = true;
      try {
        let res = await axios.get(apiPath +'/log_scrape_erank')
        this.logContent = res.data.data;
      } catch (error) {
        // eslint-disable-next-line
        alert(error.toString());
      } finally {
        this.loading = false;
      }
    },
    async clearLog(evt) {
      this.loading = true;
      try {
        await axios.post(apiPath+'/clear_log_scrape_erank', {})
        this.logContent = '';
      } catch (err) {
        console.log(err);
      } finally {
        this.loading = false;
      }
    },

  },
  async created() {
    this.onSelectOption('Use Default')
    this.loading = true;
    await this.getKeywords();
    this.loading = false;
    let vm = this;

    $('#modalDelete').on('hide.bs.modal', function (e) {
      vm.clearForm();
    });
  },
};
</script>

<template>
  <img src="/assets/loading1.gif" v-if="loading"
    style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 9999; width: 100px; height: 100px;" />

  <!-- Modal -->
  <div class="modal fade" id="modalDelete" tabindex="-1" role="dialog" aria-labelledby="modalDeleteLabel"
    aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Alert</h5>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <p v-if="!loading">Do you want to delete it?</p>
          <p v-if="loading">loading, wait for server to complete.!!</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
          <button type="button" class="btn btn-primary" @click="deleteKeyword()">Accept</button>
        </div>
      </div>
    </div>
  </div>
  <!-- create a boostrap card-->


  <div class="container">


    <h1 :style="'color:white;'">
      Export Scaper Erank Statistics</h1>
    <!-- <pre>
      {
      pages: {{ this.pages }}
      listings: {{ this.listings }}
      cookie_erank: {{ this.cookie_erank }}
      loading: {{ this.loading }}
      }
    </pre> -->


    <ul class="nav nav-tabs bg-white" id="tabs" role="tablist">
      <li class="nav-item">
        <a class="nav-link active" id="keyword-tab" data-toggle="tab" href="#keyword" role="tab" aria-controls="keyword"
          aria-selected="true" :aria-disabled="loading">Keywords</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" id="export-tab" data-toggle="tab" href="#export" role="tab" aria-controls="export"
          aria-selected="false" :aria-disabled="loading">Export</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" id="logs-tab" data-toggle="tab" href="#logs" role="tab" aria-controls="logs"
          aria-selected="false" @click="loadLog()">Logs</a>
      </li>
    </ul>
    <div class="tab-content" id="tabsContent">
      <div class="tab-pane fade show active" id="keyword" role="tabpanel" aria-labelledby="keyword-tab">
        <div class="card">
          <div class="card-body">


            <div class="row">
              <div class="card col-md-6">
                <div class="card-body">
                  <!-- KEYWORD FORM-->
                  <form @submit.prevent="createKeyword">
                    <fieldset>

                      <div class="form-group">
                        <label for="keyword">Keyword</label>
                        <!-- INPUT -->
                        <input type="keyword" class="form-control" :class="{ 'disabled': loading }" id="keyword"
                          aria-describedby="create keyword" placeholder="Enter keyword" style="width:50%"
                          v-model="formData.name" :disabled="loading">
                      </div>

                      <div class="form-group">
                        <label class="mr-2">{{  'Status ' }}</label>
                        <!-- INPUT -->
                        <input type="checkbox" v-model="formData.is_active"/>
                      </div>
                    </fieldset>

                    <button type="submit" class="btn btn-primary mr-2" :class="{ 'disabled': loading }"
                      :disabled="loading" @click="saveKeyword()">Save</button>
                    <button class="btn btn-danger" @click="clearForm()" :class="{ 'disabled': loading }"
                      :disabled="loading">Clear</button>

                  </form>

                  <!-- KEYWORD FORM-->

                </div>
              </div>
            </div>
            <!-- table section-->
            <div class="row" style="margin-top:10px">
              <table class="table table-hover table-bordered col-md-12">
                <thead>
                  <tr>
                    <th scope="col">Id</th>
                    <th scope="col">Keyword</th>
                    <th scope="col">Status</th>
                    <th scope="col">Actions</th>
                  </tr>
                </thead>
                <tbody>

                  <tr v-for="(data, index) in keywords" :key="index">
                    <td>{{ data.id }}</td>
                    <td>{{ data.name }}</td>
                    <td>{{ data.is_active ? 'Active' : 'Disabled' }}</td>
                    <td>
                      <div class="btn-group" role="group">
                        <button type="button" class="btn btn-warning btn-sm" @click="editKeyword(data)"
                          :class="{ 'disabled': loading }" :disabled="loading">Update</button>
                        <button type="button" class="btn btn-danger btn-sm" @click="openModalDelete(data)"
                          :class="{ 'disabled': loading }" :disabled="loading" data-target="#modalDelete"
                          data-toggle="modal">Delete</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <!-- table section-->
            </div>



          </div>

        </div>
      </div>
      <div class="tab-pane fade" id="export" role="tabpanel" aria-labelledby="export-tab">

        <div class="card">
          <div class="card-body">
            <div class="row">
              <div class="col-md-8">



                <h3 class="mt-3">PARAMETERS</h3>

                <div class="mt-2">
                  <div class="dropdown">
                    <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton"
                      data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                      {{ this.optionSelected || 'Options' }}
                    </button>
                    <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                      <a class="dropdown-item" href="#" @click="onSelectOption('Use Default')">Use Default</a>
                      <a class="dropdown-item" href="#" @click="onSelectOption('Custom')">Custom</a>
                      <a class="dropdown-item" href="#" @click="onSelectOption('Test')">Test</a>
                    </div>
                  </div>
                </div>

                <div class="mt-2">
                  <label>KEYWORD URL FORMAT </label>
                  <input type="text" class="form-control"  disabled="disabled" id="keyword_url"
                    aria-describedby="keyword url"  v-model="keyword_url" :disabled="loading || optionSelected == 'Use Default' || optionSelected == 'Test'">
                  <p class="warning"></p>
                </div>

                <div>
                  <label>Page per keyword </label>
                  <NumberSelect @number-selected="onPagePerKeyword" :class="{ 'disabled': loading }" :value="pages"
                    :disabled="loading || optionSelected == 'Use Default' || optionSelected == 'Test'" :min="1" :max="8"></NumberSelect>
                </div>

                <div>
                  <label>Listing per page </label>
                  <NumberSelect @number-selected="onListingPerPage" :class="{ 'disabled': loading }" :value="listings"
                    :disabled="loading || optionSelected == 'Use Default' || optionSelected == 'Test'" :min="1" :max="64"></NumberSelect>

                </div>
                <div>
                  <label>Cookie text</label>
                  <textarea :class="{ 'disabled': loading }" :disabled="loading" class="form-control"
                    v-model="cookie_erank" rows="3"></textarea>
                </div>

                <div class="mt-3">

                  <button type="button" class="btn btn-primary mr-2" :class="{ 'disabled': loading }"
                    :disabled="loading" @click="openErank()">Open Erank</button>

                  <button type="button" class="btn btn-success" :class="{ 'disabled': loading }" :disabled="loading || keywords.length == 0"
                    @click="exportkeywords()">Export</button>

                </div>


              </div>
            </div>

          </div>
        </div>



      </div>
      <div class="tab-pane fade" id="logs" role="tabpanel" aria-labelledby="logs-tab">
        <!-- boostrap card-->
        <div class="card">
          <div class="card-body">
            <div class="row">
              <div class="col-md-12">

                <h3 class="mt-3">Log</h3>
                <br/>
                <button class="btn btn-primary" @click="clearLog()">Clear Logs</button>
                <br/>
                <pre>
                  {{ logContent }}
                </pre>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>



    <!-- <h3 v-if="loading" class="text-primary">loading, wait for the database to complete.!!</h3> -->


  </div>
</template>