import os
import csv
import collections
import traceback
import SimpleITK as sitk
from radiomics import signatures


def main():
    outPath = r'E:\Git-Repos\PyRadiomicsNKI\pyradiomics-API'

    inputCSV            = outPath + os.path.sep + "TestCases.csv"
    outputFilepath      = outPath + os.path.sep + "radiomics_features.csv"
    progress_filename   = outPath + os.path.sep + "pyrad_log.txt"

    print "Loading CSV"

    flists = []
    try:
        with open(inputCSV, 'rb') as inFile:
            cr = csv.reader(inFile, lineterminator= '\n')
            flists = [row for row in cr]
    except Exception:
        with open(progress_filename,mode='a') as printfile:
            printfile.write('\tFAILED%s\n\n' %(traceback.format_exc()))

    print "Loading Done"
    print ("Patients: " + str(len(flists)))

    kwargs = {}
    kwargs['binWidth'] = 25
    kwargs['resampledPixelSpacing'] = None #[3,3,3]
    kwargs['interpolator'] = sitk.sitkBSpline
    kwargs['padDistance'] = 5
    kwargs['padFillValue'] = 0
    kwargs['verbose'] = True

    Sig = signatures.RadiomicsSignature(**kwargs)
    Sig.enableInputImages(original= {})
    #Sig.enableInputImages(wavelet= {'level': 2})
    for idx, entry in enumerate(flists, start= 1):

        with open(progress_filename,mode='a') as printfile:
            print "(%s/%s) Processing Patient: %s, Study: %s, Reader: %s" %(str(idx), str(len(flists)), entry[0], entry[1], entry[2])
            printfile.write("(%s/%s) Processing Patient: %s, Study: %s, Reader: %s\n" %(str(idx), str(len(flists)), entry[0], entry[1], entry[2]))

        imageFilepath = entry[3]
        maskFilepath = entry[4]

        if (imageFilepath is not None) and (maskFilepath is not None):
            featureVector = collections.OrderedDict()
            featureVector['PatientID'] = entry[0]
            featureVector['Study'] = entry[1]
            featureVector['Reader'] = entry[2]
            featureVector['image'] = os.path.basename(imageFilepath)
            featureVector['mask'] = os.path.basename(maskFilepath)

            try:
                featureVector.update(Sig.computeSignature(imageFilepath, maskFilepath))

                with open(outputFilepath, 'ab') as outputFile:
                    writer = csv.writer(outputFile, lineterminator = '\n')
                    if idx==1: writer.writerow(featureVector.keys())
                    writer.writerow(featureVector.values())
            except Exception:
                with open(progress_filename,mode='a') as printfile:
                    printfile.write('\tFAILED%s\n\n' %(traceback.format_exc()))

main()