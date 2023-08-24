var API_HOST = process.env.API_HOST;
var API_PORT = process.env.API_PORT;
if (API_HOST === undefined){
    API_HOST = "http://54.70.121.78"
}
if (API_PORT === undefined){
    API_PORT = "8001"
}
const Configs = {
    API_URL: `${API_HOST}:${API_PORT}`,
}
export default Configs;