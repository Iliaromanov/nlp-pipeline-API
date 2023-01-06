import * as cdk from 'aws-cdk-lib';
import { Duration, CfnOutput } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import { Construct } from 'constructs';


// For apigw throttling options to limit requests/second 
//  and avoid unwated billing issues and apply
//  token-buck style throttling to web app
//  (https://en.wikipedia.org/wiki/Token_bucket)
const MAX_RPS = 100; 
const MAX_RPS_BUCKET_SIZE = 1000;


export class NlPpipelineApiCdkAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // IAM role for lambda which grants access to logs and cloudwatch metrics
    let lambdaRole = new iam.Role(this, "LambdaRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
      inlinePolicies: {
        "lambda-executor": new iam.PolicyDocument({
          assignSids: true,
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                "ec2:DescribeTags",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
              ],
              resources: ["*"]
            }),
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ["lambda:InvokeFunction"],
              resources: ["*"]
            })
          ]
        })
      }
    });

    // Defining lambda
    let apiLambda = new lambda.Function(this, "NlpLambda", {
      functionName: "nlp-pipeline-lambda",
      code: lambda.Code.fromAsset(__dirname + "/../build-python"), // creating by make
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: "serverless_fastapi.lambda.lambda_handler",
      role: lambdaRole,
      timeout: Duration.seconds(30),
      memorySize: 256,
      // logRetention: logs.RetentionDays.SIX_MONTHS, // default is infinite
    })

    // Defining apigw lambda interface
    let apigwRestApi = new apigw.LambdaRestApi(this, "NlpPipelineLambdaRestApi", {
      restApiName: "nlp-pipeline-api",
      handler: apiLambda,
      deployOptions: {
        throttlingBurstLimit: MAX_RPS_BUCKET_SIZE,
        throttlingRateLimit: MAX_RPS
      }
    });
    const restApiUrl = `${apigwRestApi.restApiId}.execute-api.${this.region}.amazonaws.com`;

    
  }
}
