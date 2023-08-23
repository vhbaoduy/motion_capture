import Button from '@mui/material/Button';
import React, { Component } from 'react';
import Wrapper from './components/Wrapper';
import NavBar from './components/NavBar';
import ReactPlayer from 'react-player';
import myVideo from './demo/demo.mp4';


class App extends Component {

	state = {

		// Initially, no file is selected
		selectedFile: null
	};

	// On file select (from the pop up)
	onFileChange = event => {

		// Update the state
		this.setState({ selectedFile: event.target.files[0] });

	};


	// File content to be displayed after
	// file upload is complete
	fileData = () => {

		if (this.state.selectedFile) {

			return (
        <div class="video-wrapper">
					<ReactPlayer
            url= {myVideo}
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

    const handleConvertButtonClick = () => {
      if (this.state.selectedFile == undefined) {
        alert("Please upload a file first!");
      }
      else {

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
          {this.fileData()}
        </div>
      </Wrapper>

      <Wrapper class="second-box" style="display: none">
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
      </div>

      
      </div>

		);
	}
}

export default App;
