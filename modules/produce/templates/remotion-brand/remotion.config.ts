// All options: https://www.remotion.dev/docs/config
// CLI flags override these. The Node render APIs ignore this file.
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setPixelFormat('yuv420p'); // what every social platform expects
Config.setOverwriteOutput(true);
Config.setDefaultPremountInSeconds(1);
