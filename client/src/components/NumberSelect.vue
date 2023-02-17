<template>
  <div>
    <select :class="className" :value="this.value" @change="emitSelectedNumber" :disabled="disabled"  style="width: 35%;">
      <option v-for="number in numberRange" :key="number">{{ number }}</option>
    </select>
  </div>
</template>

<script>
export default {
  props: {
    "value": {
      type:Number
    },
    "class" : {
      type: String,
      default: "",
    },
    "disabled": {
      type: Boolean,
      default: false,

    },
    "min": {
      type: Number,
      default: 0,
    },
    "max": {
      type: Number,
      default: 9,
    },
  },
  data() {
    return {
    };
  },
  computed: {
    className() {
      return 'form-control ' + this.class;
    },
    numberRange() {
      return Array.from({ length: this.max }, (_, i) => i+this.min);
    },
  },
  methods: {
    emitSelectedNumber(val) {
      this.$emit("number-selected", val.target.value);
    },
  },
  created: function () {
    console.log(this.value)
  },
};
</script>
