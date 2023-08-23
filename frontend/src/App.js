import Button from '@mui/material/Button';
import React, { Component } from 'react';
import Wrapper from './components/Wrapper';
import NavBar from './components/NavBar';
import ReactPlayer from 'react-player';
// import myVideo from './demo/demo.mp4';
import axios from "axios";
import { getNativeSelectUtilityClasses } from '@mui/material';


class App extends Component {

	state = {

		// Initially, no file is selected
		selectedFile: null,
    outputFile: null,
	};

	// On file select (from the pop up)
	onFileChange = (event) => {

		// Update the state
    // console.log(event.target.files[0])
		this.setState({ selectedFile: event.target.files[0] });

	};


	// File content to be displayed after
	// file upload is complete
	fileData = (file) => {

		if (file) {

			return (
        <div class="video-wrapper">
					<ReactPlayer
            url= {URL.createObjectURL(file)}
            width="640px"
            height="360px"
            controls={true}
          />
        </div>
			);
		}
	};

  outputData = () => {
    if (this.state.selectedFile) {
      return (
        <Wrapper className="second-box">
      <div>
      <h1 id="heading">
        Output
      </h1>
          {this.fileData()}
        <div>
        <Button variant="contained" color='info'>Download</Button>{' '}
        </div>
      </div>
      </Wrapper>
      )
    }
  }





	render() {

    const handleUploadButtonClick = () => {
      document.getElementById('fileInput').click();
    };

    const handleConvertButtonClick = async () => {
      if (this.state.selectedFile == undefined) {
        alert("Please upload a file first!");
      }
      else {
          const formData = new FormData()
          console.log(this.state.selectedFile)
          await formData.append("video_file", this.state.selectedFile)
          console.log(formData)
          await axios({
            url:'54.70.121.78:8000/video',
            method: "POST",
            data:formData,
            headers:{
              'Content-Type': 'multipart/form-data'
            },
            responseType: 'blob',
          }).then(async (res) => {
            console.log(res)
            // const blob = await res.blob()
            // const dataBlob = new Blob([res.data], {type:"video/mp4"})
            // const blobURL = URL.createObjectURL(dataBlob)
            // console.log(dataBlob)
            // console.log(blobURL)
            this.setState({ outputFile: res.data });
          })
          // callApi(this.state.selectedFile)

      }
    };

		return (
      <div>
      <NavBar></NavBar>
      <div class="box">
      <Wrapper class="first-box">
      <div>
      <h1 id="heading">
        3D Pose Estimation
      </h1>
      <h2 id="heading-2">
        Upload an image to get started!
      </h2>
      <div>
        <Button variant="contained" onClick={handleUploadButtonClick}>
          Upload!
        </Button>{' '}
        <input type="file"
                id="fileInput"
                style={{ display: 'none' }}
                onChange={this.onFileChange}>

        </input>
        <Button variant="contained" color='secondary' onClick={handleConvertButtonClick}>
          Convert
        </Button>{' '}
        
        </div>
          {this.fileData(this.state.selectedFile)}
        </div>
      </Wrapper>

      <Wrapper class="second-box" style="display: none">
      <div>
      <h1 id="heading">
        Output
      </h1>
          {this.fileData(this.state.outputFile)}
        <div>
        <Button variant="contained" color='info'>Download</Button>{' '}
        </div>
      </div>
      </Wrapper>
      </div>

      
      </div>

		);
	}
}

export default App;
