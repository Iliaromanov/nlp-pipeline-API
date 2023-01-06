import * as cdk from 'aws-cdk-lib';
import { Duration, CfnOutput } from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
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

    // Fronting the API with CloudFront to:
    // 1. Remove stage name prefix from url (eg. /prod/my-url => /my-url)
    // 2. For caching responses
    if (this.node.tryGetContext("stage") !== "dev") { // no need for cdn in dev
      let cdn = new cloudfront.Distribution(this, "CDN", {
        defaultBehavior: {
          // CloudFront function to modify "Host" header to pass to lanbda; modifies
          //  the request object and puts "Host" value into "x-forwarded-host" to allow
          //  access from lambda. (needed because apigw overwrites the "Host" field)
          // https://stackoverflow.com/questions/39222208/forwarding-cloudfront-host-header-to-api-gateway
          functionAssociations: [{
            eventType: cloudfront.FunctionEventType.VIEWER_REQUEST,
            function: new cloudfront.Function(this, "RewriteCdnHost", {
              functionName: `${this.account}${this.stackName}RewriteCdnHostFunctionProd`,
              // documentation: 
              //https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/functions-event-structure.html#functions-event-structure-example
              code: cloudfront.FunctionCode.fromInline(`
              function handler(event) {
                var req = event.request;
                if (req.headers['host']) {
                  req.headers['x-forwarded-host'] = {
                    value: req.headers['host'].value
                  };
                }
                return req;
              }
              `)
            })
          }],
          origin: new origins.HttpOrigin(restApiUrl, {
            originPath: "/prod",
            protocolPolicy: cloudfront.OriginProtocolPolicy.HTTPS_ONLY,
            connectionAttempts: 3,
            connectionTimeout: Duration.seconds(10),
            httpsPort: 443,
          }),
          smoothStreaming: false,
          viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          compress: true,
          cachePolicy: new cloudfront.CachePolicy(this, 'DefaultCachePolicy', {
              // need to be overriden because the names are not automatically randomized across stages
              cachePolicyName: `CachePolicy-prod`,
              headerBehavior: cloudfront.OriginRequestHeaderBehavior.allowList("x-forwarded-host"),
              // allow Flask session variable
              cookieBehavior: cloudfront.CacheCookieBehavior.allowList("session"),
              queryStringBehavior: cloudfront.CacheQueryStringBehavior.all(),
              maxTtl: Duration.hours(1),
              defaultTtl: Duration.minutes(5),
              enableAcceptEncodingGzip: true,
              enableAcceptEncodingBrotli: true
          }),
        },
        //https://notes.serverlessfirst.com/public/What+Pricing+Class+should+I+choose+for+a+CloudFront+distribution
        priceClass: cloudfront.PriceClass.PRICE_CLASS_100, // North America + Europe
        enabled: true,
        httpVersion: cloudfront.HttpVersion.HTTP2,
      });
      new CfnOutput(this, "CDNDomain", {
        value: "https://" + cdn.distributionDomainName
      });
    }
  }
}
