import { Component } from '@angular/core';
import { SharedService } from './services/shared.service';
import { ChartOptions, ChartType } from 'chart.js';
import { Label, SingleDataSet } from 'ng2-charts';

class FileObject {
  constructor(public src: string, public file: File) {
  }
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  file: File = null;
  selectedFile: FileObject;
  data: any = [];
  msg: string = "";
  status: string = "";
  acroynms = [];
  filtredAcroynms = [];
  allAcroynms = [];
  selectedAcronym: string = "";
  fullForm: string = "";
  toggleTable: boolean;
  constructor(private sharedSvc: SharedService){

  }
  
  ngOnInit() {
    this.sharedSvc.getAllAcronyms()
    .subscribe(
      (data: any) => { this.allAcroynms = data.data },
      (err) => {console.log(err); }
    )
  }

  closeAlert(){
    this.status = "";
  }
  
  getFullForm(acronym: string){
    if(acronym === ""){
      this.msg = "Please enter acronym";
      this.status = "danger";
      return;
    } 
    this.filtredAcroynms = [];
    this.sharedSvc.getAcronymFullForm(acronym)
    .subscribe(
      (data: any) => {
        this.fullForm = data.data;
        this.msg = data.msg;
        this.status = data.status;
        if(this.fullForm === ""){
          this.msg = "No full form found";
          this.status = "warning";
        }
        if(this.status == "error"){
          this.status = "danger";
        }
      },
      (err) => {
        this.msg = "Error getting full-form";
        this.status = "danger";
        console.log(err);
      }
    );
  }

  selectAcronym(acronym: string){
    this.selectedAcronym = acronym;
    this.filtredAcroynms = [];
  }

  search(query: string) {
    this.fullForm = "";
    let result: any = this.select(query.toLowerCase());
    this.filtredAcroynms = result;
  }

  select(query: string): string[] {
    let result: string[] = [];
    for (let a of this.allAcroynms) {
      if (a.toLowerCase().indexOf(query) > -1) {
        result.push(a)  
      }
    }
    return result
  }

  processFile(fileInput){
    console.log("selected file");
    this.file = fileInput.files[0];
    if(this.file){
      console.log(this.file);
      this.msg = "file is loaded";
      this.status = "info";
    }
  }

  uploadTextFile(){
    this.toggleTable = true;
    if(!this.file){
      this.msg = "Please select file";
      this.status = "danger";
      return;
    } 
    console.log("uploading text file");
    this.sharedSvc.uploadFile("text-file", this.file)
    .subscribe(
      (data: any) => {
        if(data.data){
          this.data = data.data;
        }
        this.msg = data.msg;
        this.status = data.status;
      },
      (err) => {
        this.msg = "Error creating Corpus";
        this.status = "danger";
        console.log(err);
      }
    );
  }

  uploadResumeFile(){
    this.toggleTable = false;
    if(!this.file){
      this.msg = "Please select file";
      this.status = "danger";
      return;
    } 
    console.log("uploading resume file");
    this.sharedSvc.uploadFile("resume-file", this.file)
    .subscribe(
      (data: any) => {
        if(data.data){
          this.acroynms = data.data;
        }
        this.msg = data.msg;
        this.status = data.status;
      },
      (err) => {
        this.msg = "Error getting Acronyms";
        this.status = "danger";
        console.log(err);
      }
    );
  }
  
  // bar chart
  public pieChartOptions: ChartOptions = {
    responsive: true,
  };
  public pieChartLabels: Label[] = ['found', 'not found'];
  public pieChartData: SingleDataSet = [40, 160];
  public pieChartType: ChartType = 'pie';
  public pieChartLegend = true;
  public pieChartPlugins = [];



}
