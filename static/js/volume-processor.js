class VolumeProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        const input = inputs[0];
        let sum = 0;
        let inputLength = input[0].length;
        for (let i = 0; i < inputLength; ++i) {
            sum += input[0][i] * input[0][i];
        }
        let rms = Math.sqrt(sum / inputLength);
        this.port.postMessage({ volume: rms * 100 });
        return true;
    }
}
registerProcessor('volume-processor', VolumeProcessor);