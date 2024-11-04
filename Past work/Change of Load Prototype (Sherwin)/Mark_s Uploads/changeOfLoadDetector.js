// The underlying problem is to identify the change of load from our smart
// outlet (PLC) devices; that is, we want to know if the appliance that is
// currently connected to the PLC device has been switched out with another
// appliance (e.g., Coffee Maker to Printer). Obviously, these devices may or
// may not operate at the same power level (watts) and each device may operate
// within its own different phases (in-use, idle, etc.).
//
// So, one of the main problem lies in detecting whether the change in power
// signature means simply the current appliance operated at another phase (e.g.,
// idle to in-use; resulting higher power consumption), or the appliance changed
// altogether.
//
// We must infer this information only using data from our timeseries database
// (Influx) which gives us constant readings (by the second) from the smart
// outlets installed in the field.
//
// Things to remember:
// - The power consumption readings are in milliwatts.
// - The data stream is updated every second (but not strictly, we may choose to
//   aggregate to a higher granularity for better performance).
// - The data stream is continuous but may contain gaps in time (e.g., when the device
//   is offline or non-communicating).
// - The data stream may contain multiple devices (smart outlets) and we need to
//   detect the change of load for each device. i.e., different set of
//   device_ids.
//   - Though, we may choose to focus on a single device for now and it is best to
//     implement the algorithm for a single device first.
//
// Good to know (we already have algorithm to detect this):
// - When the power consumption readings are zero, the PLC is unused or there is
//   no appliance connected to it.




// ************* Change of Load Detection Algorithm ************* //

/**
 * Detects the change of load of the smart outlet.
 * @param {Array} data - The stream of data readings from the smart outlet.
 *
 * Sample data stream of a single device updated every second:
 * data = [
 *  {
 *    device_id:  '563672',
 *    start_time: '2024-07-30:00:00Z',
 *    stop_time:  '2024-08-06T00:00:00Z',
 *    time:       '2024-07-31T00:00:01Z',
 *    value:      '131061'
 *  },
 *  {
 *    device_id:  '563672',
 *    start_time: '2024-07-30:00:00Z',
 *    stop_time:  '2024-08-06T00:00:00Z',
 *    time:       '2024-07-31T00:00:02Z',
 *    value:      '162186'
 *  },
 *  {
 *    device_id:  '563672',
 *    start_time: '2024-07-30:00:00Z',
 *    stop_time:  '2024-08-06T00:00:00Z',
 *    time:       '2024-07-31T00:00:03Z',
 *    value:      '162010'
 *  },
 *  ...
 * ]
 *
 * device_id:  The unique identifier of the smart outlet.
 * start_time: The start time of the data stream.
 * stop_time:  The stop time of the data stream.
 * time:       The timestamp of the data reading.
 * value:      The power consumption value in milliwatts.
 *
 * @returns {boolean} - True if the load has changed, false otherwise.
 */
function detectChangeOfLoad(data) {

  // TODO: Implement the change of load detection algorithm

}





// ************* Naive Approach Implementation ************* //
// This is a naive approach to detect the change of load of the smart outlet.
// It uses a simple moving average and deviation threshold to detect the change
// in power consumption. This approach is simple and may not be suitable for
// all scenarios, but it provides a starting point for further improvements.

/**
 * Detects the change of load of the smart outlets
 * @param {Array} data - The stream of data readings from the smart outlets.
 * @params.data is the response from queryData
 * @params.deviceIds is the list of deviceIds to check
 * @params.timeRangeStart is the start date of the time range (yyyy-MM-dd)
 * @params.timeRangeStop is the stop date of the time range (yyyy-MM-dd)
 * @returns {Array} - List of objects containing the device_id, date, and value
 *                    of the detected potential change of load.
 */
export const naiveDetectChangeOfLoad = (params) => {
  // Flux data structure:
  // [
  //  {
  //    device_id: "563672"
  //    host: "prod-kafka-mqtt-stack"
  //    result: "_result"
  //    table: 0
  //    _field: "analogInput_3"
  //    _measurement: "Smart_Plugs_Bert"
  //    _start: "2024-07-11T00:00:00Z"
  //    _stop: "2024-07-25T00:00:00Z"
  //    _time: "2024-07-11T00:56:55.579801399Z"
  //    _value: 51870
  //  },
  //  ...
  //  {
  //    device_id: "123761"
  //    host: "prod-kafka-mqtt-stack"
  //    result: "_result"
  //    table: 0
  //    _field: "analogInput_3"
  //    _measurement: "Smart_Plugs_Bert"
  //    _start: "2024-07-11T00:00:00Z"
  //    _stop: "2024-07-25T00:00:00Z"
  //    _time: "2024-07-11T00:56:55.579801399Z"
  //    _value: 12237
  //  }, ...
  // ]
  const fluxData = params.data;

  // Handle changed devices (deviation of at least 20% from the mean value)
  // Not using datedData because we need to calculate moving average, so create
  // a new structure to only group values by device

  const changeDetected = [];

  // Group values by device
  const deviceValues = {};
  fluxData.forEach(row => {
    if (!deviceValues[row.device_id]) deviceValues[row.device_id] = [];
    deviceValues[row.device_id].push({
      value: parseFloat(row._value),
      date: row._time
    });
  });

  // Loop through each data point for each device and calculate moving average
  // along with the deviation from the moving average as the loop increments. If
  // the deviation is more than 50%, then flag it as changed device.

  const deviationThreshold = 50;
  for (const deviceId in deviceValues) {
    let dataCount = 0;
    let sum = 0;
    let movingAverage = 0;
    let changed = false;

    for (let i = 0; i < deviceValues[deviceId].length; i++) {
      // ignore value of 0 for now. Unnecessary noise

      if (deviceValues[deviceId][i].value === 0) {
        continue;
      }

      const value = deviceValues[deviceId][i].value;
      sum += value;
      dataCount++;
      movingAverage = sum / dataCount;

      const deviation = Math.abs((value - movingAverage) / movingAverage) * 100;
      if (deviation >= deviationThreshold) {
        changed = true;
      }

      if (changed) {
        changeDetected.push({ deviceId, date: fluxData[i]._time, value: value.toFixed(2) });
        changed = false;
      }
    }
  }

  return changeDetected;
};
